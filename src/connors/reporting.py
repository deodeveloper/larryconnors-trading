import json,html
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
from .plotting import dark_theme

def episodes(orders):
    rows=[]
    for symbol,g in orders[orders.status=='filled'].groupby('symbol',sort=False):
        state=None
        for r in g.itertuples():
            if state is None:
                state=dict(symbol=symbol,entry=r.timestamp,entry_notional=0.,pnl=0.,entries=0,quantity=0.)
            state['pnl']-=r.quantity*r.price+r.fees;state['quantity']+=r.quantity
            if r.action!='exit':state['entry_notional']+=abs(r.quantity*r.price);state['entries']+=1
            if abs(state['quantity'])<1e-8:
                state.update(exit=r.timestamp,return_on_entered_notional=state['pnl']/state['entry_notional'],holding_calendar_days=(r.timestamp-state['entry']).total_seconds()/86400)
                rows.append(state);state=None
    return pd.DataFrame(rows,columns=['symbol','entry','exit','entry_notional','pnl','entries','quantity','return_on_entered_notional','holding_calendar_days'])

def daily_equity(result):
    value=result.portfolio.value()
    if isinstance(value,pd.Series):value=value.to_frame('combined')
    if list(value.columns)==['combined']:
        value['combined']-=result.borrow_liability.sum(axis=1)
    else:value=value-result.borrow_liability
    value=value.iloc[2::3].copy();value.index=value.index.normalize()
    if 'combined' not in value:value['combined']=value.sum(axis=1)
    return value

def metrics(equity,initial,trades,orders):
    returns=equity.pct_change(fill_method=None);returns.iloc[0]=equity.iloc[0]/initial-1
    peak=equity.cummax().clip(lower=initial);drawdown=equity/peak-1
    elapsed=(equity.index[-1]-equity.index[0]).days/365.25
    wins=trades.pnl.gt(0) if len(trades) else pd.Series(dtype=bool)
    gain=trades.loc[wins,'pnl'].sum();loss=-trades.loc[~wins,'pnl'].sum()
    std=returns.std(ddof=1)
    filled=orders[orders.status=='filled']
    return dict(total_return=float(equity.iloc[-1]/initial-1),cagr=float((equity.iloc[-1]/initial)**(1/elapsed)-1) if elapsed>=1 and equity.iloc[-1]>0 else None,max_drawdown=float(drawdown.min()),sharpe=float(returns.mean()/std*np.sqrt(252)) if std>0 else None,completed_episodes=len(trades),win_rate=float(wins.mean()) if len(trades) else None,average_trade_return=float(trades.return_on_entered_notional.mean()) if len(trades) else None,profit_factor=float(gain/loss) if loss>0 else None,turnover=float((filled.quantity.abs()*filled.price).sum()/equity.mean()),mean_holding_calendar_days=float(trades.holding_calendar_days.mean()) if len(trades) else None)

def export(result,path,quality=None):
    out=Path(path);out.mkdir(parents=True,exist_ok=True)
    eq=daily_equity(result);trades=episodes(result.orders);ex=result.config.get('execution',{})
    initial=ex.get('initial_capital',100000)*(1 if ex.get('shared_cash',True) else len(result.bars))
    stats=metrics(eq.combined,initial,trades,result.orders)
    assets=result.portfolio.assets();asset_values=assets*result.marks
    exposure=asset_values.abs().sum(axis=1).iloc[2::3].to_numpy()/eq.combined
    curves=eq.copy();curves['drawdown']=eq.combined/eq.combined.cummax().clip(lower=initial)-1;curves['gross_exposure']=exposure
    # Equal-weight buy and hold, same price adjustment, fees, slippage and initial capital.
    import vectorbt as vbt
    close=pd.DataFrame({s:b.close.reindex(eq.index) for s,b in result.bars.items()})
    mode=ex.get('mode','source_close');first_price=pd.Series({s:(b.open if mode=='next_open' else b.close).loc[eq.index[0]] for s,b in result.bars.items()})
    sizes=pd.DataFrame(0.,index=close.index,columns=close.columns)
    sizes.iloc[0]=(initial/len(close.columns))/(first_price*(1+ex.get('fees',.0005))*(1+ex.get('slippage',.0005)))
    prices=close.copy();prices.iloc[0]=first_price
    bh=vbt.Portfolio.from_orders(close,size=sizes,price=prices,init_cash=initial,cash_sharing=True,group_by=True,fees=ex.get('fees',.0005),slippage=ex.get('slippage',.0005),freq='1D')
    curves['buy_hold']=bh.value().to_numpy()
    # Shared-cash per-symbol results are P&L contributions, not standalone return ratios.
    per=[]
    for s in result.bars:
        o=result.orders[(result.orders.symbol==s)&(result.orders.status=='filled')]
        realized_cash=-(o.quantity*o.price+o.fees).sum()
        end_value=asset_values[s].iloc[-1]
        per.append(dict(symbol=s,pnl_including_open=float(realized_cash+end_value-result.borrow_liability[s].iloc[-1]),completed_episodes=int((trades.symbol==s).sum()),denominator='P&L contribution; shared cash has no independent symbol return denominator'))
    result.orders.to_csv(out/'orders.csv',index=False);trades.to_csv(out/'trades.csv',index=False);curves.to_csv(out/'curves.csv');pd.DataFrame(per).to_csv(out/'per_symbol.csv',index=False)
    payload=dict(metrics=stats,config=result.config,parameters=result.parameters,source=result.spec,data_quality=quality or {},conventions=dict(sharpe='252 daily observations, arithmetic excess returns, zero risk-free, sample std',cagr='Actual calendar years; omitted below one year',trade_return='Net closed episode P&L / sum of entry notionals; scaled entries count as one episode',turnover='Two-way filled notional / mean equity, not annualized',holding='Calendar days, includes intraday fraction',open_positions='Marked to final close, excluded from win rate and profit factor',costs='Proportional fees and adverse market slippage; limit price caps slippage',borrow='Annual configured rate, ACT/365 on previous close short market value; accrued liability deducted from reported equity, settled as vectorbt exit fee'))
    (out/'summary.json').write_text(json.dumps(payload,indent=2,default=str,allow_nan=False))
    parts=['<html><head><meta charset="utf-8"><title>Connors research</title><style>body{background:#111827;color:#e5e7eb;font-family:system-ui,sans-serif;margin:24px}a{color:#93c5fd}pre{white-space:pre-wrap}</style></head><body>', '<h1>Connors research report</h1>', '<p>'+html.escape(result.config['data'].get('provider','synthetic').upper()+' — '+ex.get('mode','source_close'))+'</p>', '<p>Source-close uses idealized completed-bar same-close fills. Synthetic results are not real-market evidence.</p>']
    for i,(columns,title) in enumerate([(['combined','buy_hold'],'Equity and equal-weight buy-and-hold'),(['drawdown'],'Drawdown'),(['gross_exposure'],'Gross exposure')]):
        fig=dark_theme(px.line(curves,x=curves.index,y=columns,title=title))
        parts.append(fig.to_html(full_html=False,include_plotlyjs=True if i==0 else False))
    parts.extend(['<pre>'+html.escape(json.dumps(payload,indent=2,default=str))+'</pre>','</body></html>'])
    (out/'report.html').write_text('\n'.join(parts));return payload
