import pandas as pd
from connors.hpe.strategy import signals
from connors.short_term.strategy import signals as short_signals
from connors.strategies import add_allowed,resolve

def fixture():
    b=pd.DataFrame(dict(close=[100.]*8,high=[110,109,108,107,106,105,104,103],low=[100,99,98,97,96,95,94,93],volume=[2e6]*8))
    f=pd.DataFrame(dict(sma200=[90.]*8,sma5=[101.]*8,rsi2=[25.]*8,rsi4=[25.]*8,b=[.2]*8))
    return b,f

def test_strict_thresholds():
    b,f=fixture();en,ex=signals('rsi4',b,f,dict(entry=25,exit=55),1)
    assert not en.any()
    f.rsi4=24.999;assert signals('rsi4',b,f,dict(entry=25,exit=55),1)[0].all()
    f.rsi4=55.;assert not signals('rsi4',b,f,dict(entry=25,exit=55),1)[1].any()

def test_three_high_low_comparisons_require_four_bars():
    b,f=fixture();en,_=signals('high_low',b,f,{},1)
    assert not en.iloc[:3].any();assert en.iloc[3]

def test_double_seven_inclusive_current_window():
    b,f=fixture();en,ex=short_signals('double7',b,f,{},None)
    assert not en.iloc[:6].any();assert en.iloc[6];assert ex.iloc[6]

def test_tps_equality_trend_add_and_last_fill():
    b,f=fixture();spec,p=resolve('hpe.tps.long');b.loc[7,'close']=90
    assert add_allowed(spec,p,b,f,7,last=91,first=101)
    b.loc[7,'close']=89;assert not add_allowed(spec,p,b,f,7,last=91,first=101)
    b.loc[7,'close']=95;assert not add_allowed(spec,p,b,f,7,last=94,first=101)

def test_percent_b_three_strict_days():
    b,f=fixture();assert not signals('percent_b',b,f,{},1)[0].any()
    f.b=.19;assert signals('percent_b',b,f,{},1)[0].iloc[2]

def test_tps_two_closes_not_one():
    b,f=fixture();f.rsi2=[26,24,26,24,24,25,24,24]
    en,_=signals('tps',b,f,{},1)
    assert list(en)==[False,False,False,False,True,False,False,True]

def test_short_threshold_and_trend_restriction():
    b,f=fixture();b.close=80.;f.rsi4=75.
    assert not signals('rsi4',b,f,dict(entry=75,exit=45),-1)[0].any()
    f.rsi4=76.;assert signals('rsi4',b,f,dict(entry=75,exit=45),-1)[0].all()
    spec,p=resolve('hpe.tps.short');b.loc[7,'close']=91
    assert not add_allowed(spec,p,b,f,7,last=85,first=83)
    b.loc[7,'close']=90;assert add_allowed(spec,p,b,f,7,last=85,first=83)

def test_catalog_copies_match_and_blocks_cannot_be_overridden():
    import json
    from pathlib import Path
    import pytest
    from connors.strategies import catalog
    assert catalog()==json.loads(Path('docs/strategy_catalog.json').read_text())
    with pytest.raises(ValueError,match='BLOCKED'):resolve('buy_fear.terror_gaps',allow_experimental=True)
    with pytest.raises(ValueError,match='allow_experimental'):resolve('short_term.cumulative')
