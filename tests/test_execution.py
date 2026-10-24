import numpy as np
import pandas as pd
import pytest
from connors.data import synthetic
from connors.strategies import resolve
from connors.execution import run,limit_fill
from connors.reporting import episodes,daily_equity

def setup(strategy='hpe.tps.long',mode='source_close',prices=None):
    bars=synthetic(['S'],'2020-01-01','2022-01-31');b=bars['S'];ix=b.index[-8:]
    if prices is None:prices=[120,119,118,117,125,126,127,128]
    for k,v in zip(ix,prices):b.loc[k,['open','close']]=v;b.loc[k,'high']=v+2;b.loc[k,'low']=v-2
    cfg={'data':{'start':str(ix[0].date()),'end':str(ix[-1].date())},'execution':{'mode':mode,'initial_capital':1000,'position_fraction':.8,'fees':0,'slippage':0,'assume_borrow_available':True}}
    spec,p=resolve(strategy);en=pd.Series(False,index=b.index);en.loc[ix[0]]=True;ex=en.copy()*False;ex.loc[ix[4]]=True
    return bars,spec,p,cfg,{'S':(en,ex)},ix

def test_limit_open_improvement_touch_and_expiry():
    assert limit_fill(90,100,89,95,1)==90
    assert limit_fill(100,101,96,95,1) is None
    assert limit_fill(100,101,95,95,1)==95
    assert limit_fill(110,112,99,105,-1)==110
    assert limit_fill(100,104,99,105,-1) is None

def test_sequential_scale_full_exit_and_reference_accounting():
    bars,spec,p,cfg,sigs,ix=setup();r=run(bars,spec,p,cfg,signal_override=sigs)
    o=r.orders.query('status == "filled"');assert o.action.tolist()==['entry','add','add','add','exit']
    np.testing.assert_allclose(o.quantity.iloc[:4]*o.price.iloc[:4],[80,160,240,320])
    assert o.timestamp.dt.normalize().nunique()==5
    assert o.quantity.sum()==pytest.approx(0)
    reference=1000-(o.quantity*o.price+o.fees).sum()
    assert daily_equity(r).combined.iloc[-1]==pytest.approx(reference)
    ep=episodes(o);assert len(ep)==1;assert ep.entries.iloc[0]==4
    assert ep.pnl.iloc[0]==pytest.approx(reference-1000)

def test_next_open_shift_and_actual_fill():
    bars,spec,p,cfg,sigs,ix=setup('hpe.high_low.long','next_open');p['aggressive']=True
    bars['S'].loc[ix[1],'open']=115
    r=run(bars,spec,p,cfg,signal_override=sigs);o=r.orders.query('status == "filled"')
    assert o.iloc[0].timestamp.normalize()==ix[1];assert o.iloc[0].price==115
    # Prior closes 119,118,117 are above actual initial 115: no adverse-price add.
    assert 'add' not in o.action.tolist()
    assert o.iloc[-1].timestamp.normalize()==ix[5]

def test_exit_precedence():
    bars,spec,p,cfg,sigs,ix=setup();sigs['S'][1].loc[ix[1]]=True
    o=run(bars,spec,p,cfg,signal_override=sigs).orders
    assert o.action.tolist()==['entry','exit']

def test_short_pnl_and_cash():
    bars,spec,p,cfg,sigs,ix=setup('short_term.sp_short',prices=[100,99,98,97,90,89,88,87])
    r=run(bars,spec,p,cfg,signal_override=sigs);o=r.orders
    assert o.quantity.iloc[0]==-8;assert o.quantity.iloc[-1]==8
    assert daily_equity(r).combined.iloc[-1]==pytest.approx(1080)

def test_cash_cap_and_fees():
    bars,spec,p,cfg,sigs,ix=setup('short_term.double7');cfg['execution'].update(position_fraction=1,fees=.01,slippage=.01)
    r=run(bars,spec,p,cfg,signal_override=sigs)
    assert r.portfolio.cash().min()>=-1e-8
    assert daily_equity(r).combined.iloc[-1]==pytest.approx(1000-(r.orders.quantity*r.orders.price+r.orders.fees).sum())

def test_future_changes_cannot_change_past_orders():
    bars,spec,p,cfg,sigs,ix=setup();a=run(bars,spec,p,cfg,signal_override=sigs).orders
    bars['S'].loc[ix[-1],['open','high','low','close']]=[999,1000,998,999]
    b=run(bars,spec,p,cfg,signal_override=sigs).orders
    pd.testing.assert_frame_equal(a[a.timestamp<ix[-1]],b[b.timestamp<ix[-1]])

def test_independent_cash():
    bars,spec,p,cfg,sigs,ix=setup('short_term.double7');bars['T']=bars['S'].copy();sigs['T']=sigs['S'];cfg['execution']['shared_cash']=False
    r=run(bars,spec,p,cfg,signal_override=sigs)
    eq=daily_equity(r);np.testing.assert_allclose(eq.S,eq["T"]);np.testing.assert_allclose(eq.combined,eq.S*2)

def test_borrow_accrues_and_settles_with_short_exit():
    bars,spec,p,cfg,sigs,ix=setup('short_term.sp_short',prices=[100,99,98,97,90,89,88,87]);cfg['execution']['borrow_rate']=.365
    r=run(bars,spec,p,cfg,signal_override=sigs)
    cost=sum(8*bars['S'].close.loc[ix[i-1]]*.365*(ix[i]-ix[i-1]).days/365 for i in range(1,5))
    assert r.orders.fees.sum()==pytest.approx(cost)
    assert daily_equity(r).combined.iloc[-1]==pytest.approx(1080-cost)
    assert r.borrow_liability.iloc[5,0]>0
    assert r.borrow_liability.iloc[-1,0]==0

def test_short_requires_borrow_assumption():
    bars,spec,p,cfg,sigs,ix=setup('short_term.sp_short');cfg['execution']['assume_borrow_available']=False
    with pytest.raises(ValueError,match='borrow'):run(bars,spec,p,cfg,signal_override=sigs)

def test_overnight_uses_close_then_next_open():
    bars,spec,p,cfg,sigs,ix=setup('short_term.overnight');r=run(bars,spec,p,cfg)
    assert r.orders.action.iloc[:4].tolist()==['entry','exit','entry','exit']
    assert r.orders.phase.iloc[:4].tolist()==['close','open','close','open']
    assert len(episodes(r.orders))==7

def test_limit_is_next_session_only_and_full_exit():
    bars,_,_,cfg,sigs,ix=setup('short_term.double7')
    spec,p=resolve('buy_fear.new_highs',allow_experimental=True);p['limit_pct']=.07
    # First session signal at 120. Next session limit111.6; gap below limit -> 110.
    bars['S'].loc[ix[1],['open','high','low','close']]=[110,112,109,111]
    r=run(bars,spec,p,cfg,signal_override=sigs);o=r.orders.query('status == "filled"')
    assert o.iloc[0].price==110;assert o.iloc[0].timestamp.normalize()==ix[1]
    assert o.iloc[0].signal_date==ix[0];assert o.iloc[-1].action=='exit'

def test_unfilled_limit_expires_without_later_fill():
    bars,_,_,cfg,sigs,ix=setup('short_term.double7');spec,p=resolve('buy_fear.new_highs',allow_experimental=True)
    bars['S'].loc[ix[2],['open','high','low','close']]=[100,101,99,100]
    r=run(bars,spec,p,cfg,signal_override=sigs)
    assert r.orders.status.tolist()==['expired']

def test_rejected_allocation_does_not_advance_stages():
    bars,spec,p,cfg,sigs,ix=setup();cfg['execution']['max_gross_exposure']=.000001
    r=run(bars,spec,p,cfg,signal_override=sigs)
    # Limit constrains actual allocation; subsequent risk rejection remains in ledger.
    assert (r.orders.quantity.abs()*r.orders.price).iloc[0]<=.001001
    assert daily_equity(r).combined.iloc[-1]>0
