"""Stateful vectorbt order callbacks; state advances only on accepted fills."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
import vectorbt as vbt
from vectorbt.portfolio.nb import order_nb
from vectorbt.portfolio.enums import NoOrder,OrderStatus
from .strategies import generate,stages,add_allowed

@dataclass
class Result:
    portfolio: object
    orders: pd.DataFrame
    marks: pd.DataFrame
    bars: dict
    spec: dict
    parameters: dict
    config: dict
    borrow_liability: pd.DataFrame

def limit_fill(open_,high,low,limit,direction):
    if direction==1:return min(open_,limit) if low<=limit else None
    return max(open_,limit) if high>=limit else None

def run(bars,spec,p,cfg,aux=None,signal_override=None):
    ex=cfg.get('execution',{});mode=ex.get('mode','source_close')
    if mode not in ['source_close','next_open']:raise ValueError('Invalid execution mode')
    borrow_rate=float(ex.get('borrow_rate',0))
    if borrow_rate<0:raise ValueError('Borrow rate must be nonnegative')
    d=1 if spec['direction']=='long' else -1
    if d==-1 and not ex.get('assume_borrow_available',False):raise ValueError('Short run requires explicit assume_borrow_available; historical locates unavailable')
    kind=spec['id'].split('.')[1]
    if kind=='overnight' and mode!='source_close':raise ValueError('Overnight test requires source_close; next-open entry would erase overnight exposure')
    start=pd.Timestamp(cfg['data']['start']);end=pd.Timestamp(cfg['data']['end'])
    symbols=list(bars);features={};signals={};dates=None
    for s,b in bars.items():
        if not b.index.equals(bars[symbols[0]].index):raise ValueError('Symbols require identical complete session coverage; no silent intersection or fill')
        f,en,exit=generate(spec,b,p,aux);features[s]=f;signals[s]=(en,exit)
        if signal_override is not None:signals[s]=signal_override[s]
        dates=b.index[(b.index>=start)&(b.index<=end)]
    if dates is None or len(dates)==0:raise ValueError('Empty evaluation range')
    # Event timestamps are phase labels, not asserted exchange close times (early closes vary).
    index=pd.DatetimeIndex([day+pd.Timedelta(hours=h) for day in dates for h in [9,12,16]])
    marks=pd.DataFrame(index=index,columns=symbols,dtype=float)
    for s,b in bars.items():
        sample=b.loc[dates];marks[s]=np.column_stack([sample.open,sample.open,sample.close]).ravel()
    alloc,equal=stages(spec,p)
    if "position_steps" in ex:
        requested = ex["position_steps"]
        if len(requested)>len(alloc):raise ValueError("Position steps exceed documented scale-in stages")
        alloc=list(requested)
    if any(x<=0 for x in alloc) or not np.isclose(sum(alloc),1):raise ValueError('Stages must be positive and sum to one planned position')
    n=len(symbols);stage=np.zeros(n,int);last=np.full(n,np.nan);first=last.copy();budget=np.zeros(n);units=np.zeros(n);entered=np.full(n,-1)
    liability=np.zeros(n);liability_history=np.zeros((len(index),n))
    pending={};records=[];shared=ex.get('shared_cash',True);capital=float(ex.get('initial_capital',100000))
    if not np.isfinite(capital) or capital<=0:raise ValueError('Initial capital must be positive')
    fraction=float(ex.get('position_fraction',1/n));gross_limit=float(ex.get('max_gross_exposure',1));leverage=float(ex.get('max_leverage',1))
    if not 0<fraction<=leverage or min(gross_limit,leverage)<=0:raise ValueError('Invalid sizing constraints')
    fees=float(ex.get('fees',.0005));slip=float(ex.get('slippage',.0005))
    if fees<0 or slip<0:raise ValueError('Negative trading costs')
    def order(c):
        j=c.col;s=symbols[j];day_i=c.i//3;phase=c.i%3;day=dates[day_i];b=bars[s];loc=b.index.get_loc(day)
        f=features[s];en,exit=signals[s];held=abs(c.position_now)>1e-12
        if phase==0 and day_i>0 and c.position_now<0:
            liability[j]+=abs(c.position_now)*b.close.iloc[loc-1]*borrow_rate*(day-dates[day_i-1]).days/365
        liability_history[c.i,j]=liability[j]
        action=None;price=None;signal_i=loc
        if kind=='overnight':
            if phase==0 and held:action='exit';price=b.open.iloc[loc]
            elif phase==2 and not held:action='entry';price=b.close.iloc[loc]
        else:
            if mode=='next_open':
                if phase==0 and day_i>0:signal_i=loc-1;price=b.open.iloc[loc]
            elif phase==2:price=b.close.iloc[loc]
            if price is not None:
                if held and (exit.iloc[signal_i] or (kind=='ten_day' and day_i-entered[j]>=5+(mode=='next_open'))):action='exit'
                elif held and stage[j]<len(alloc) and add_allowed(spec,p,b,f,signal_i,last[j],first[j]):action='add'
                elif not held and kind not in ['crash','new_highs'] and en.iloc[signal_i]:action='entry'
            if phase==1 and not held and kind in ['crash','new_highs'] and day_i>0 and en.iloc[loc-1]:
                signal_i=loc-1;limit=b.close.iloc[loc-1]*(1-p['limit_pct']*d)
                price=limit_fill(b.open.iloc[loc],b.high.iloc[loc],b.low.iloc[loc],limit,d)
                if price is None:
                    records.append(dict(timestamp=index[c.i],symbol=s,action='entry',status='expired',quantity=0,price=limit,fees=0,signal_date=b.index[signal_i],phase='limit',note='DAY limit not touched'));return NoOrder
                # Slippage may consume improvement but cannot violate the limit.
                price=min(price*(1+slip),limit) if d==1 else max(price*(1-slip),limit)
                action='entry'
        if action is None:return NoOrder
        if action=='exit':qty=-c.position_now
        else:
            sl=slice(c.from_col,c.to_col);vals=marks.iloc[c.i].to_numpy()[sl]
            positions=c.last_position[sl];equity=c.cash_now+np.dot(positions,vals)-liability[sl].sum()
            if equity<=0:return NoOrder
            if action=='entry':budget[j]=equity*fraction
            want=units[j] if equal and action=='add' else budget[j]*alloc[stage[j]]/price
            room=max(0,min(gross_limit,leverage)*equity-np.dot(np.abs(positions),vals))
            # No borrowing cash to finance long buys. vectorbt additionally enforces available cash.
            want=min(want,room/(price*(1+slip+fees)))
            if d==1:want=min(want,max(0,c.cash_now)/(price*(1+slip+fees)))
            if want<=1e-12:
                records.append(dict(timestamp=index[c.i],symbol=s,action=action,status='risk_rejected',quantity=0,price=price,fees=0,signal_date=b.index[signal_i],phase=['open','limit','close'][phase],note='Cash or exposure cap'));return NoOrder
            qty=d*want
        pending[j]=(action,signal_i,day_i,phase)
        return order_nb(size=qty,price=price,fees=fees,fixed_fees=liability[j] if action=='exit' else 0,slippage=0 if phase==1 else slip,lock_cash=False,allow_partial=True,log=True)
    def post(c):
        j=c.col
        if j not in pending:return
        action,signal_i,day_i,phase=pending.pop(j);r=c.order_result;s=symbols[j]
        ok=r.status==OrderStatus.Filled
        records.append(dict(timestamp=index[c.i],symbol=s,action=action,status='filled' if ok else 'rejected',quantity=float(r.size)*(1 if r.side==0 else -1) if ok else 0,price=float(r.price) if ok else None,fees=float(r.fees) if ok else 0,signal_date=bars[s].index[signal_i],phase=['open','limit','close'][phase],note='daily OHLC assumes touch liquidity; no queue model' if phase==1 else ''))
        if not ok:return
        if action=='exit':
            stage[j]=0;last[j]=first[j]=np.nan;units[j]=0;liability[j]=0;liability_history[c.i,j]=0
        else:
            if action=='entry':first[j]=r.price;units[j]=r.size;entered[j]=day_i
            last[j]=r.price;stage[j]+=1
    pf=vbt.Portfolio.from_order_func(marks,order,post_order_func_nb=post,use_numba=False,row_wise=True,init_cash=capital,cash_sharing=shared,group_by=True if shared else False,update_value=True,ffill_val_price=False,max_orders=len(index)*n,max_logs=len(index)*n,freq='1D')
    cols=['timestamp','symbol','action','status','quantity','price','fees','signal_date','phase','note']
    return Result(pf,pd.DataFrame(records,columns=cols),marks,bars,spec,p,cfg,pd.DataFrame(liability_history,index=index,columns=symbols))
