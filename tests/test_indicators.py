import numpy as np
import pandas as pd
import pytest
from connors.indicators import rsi,streak,percent_rank,connors_rsi,cumulative_rsi,percent_b,historical_volatility,consecutive

def test_wilder_seed_and_recursion():
    x=pd.Series([10.,11,10,12,11])
    np.testing.assert_allclose(rsi(x,2).iloc[2:],[50,100*1.25/1.5,100*.625/1.25])
    assert rsi(pd.Series([1.]*5),2).iloc[-1]==50
    assert rsi(pd.Series([1.,2,3]),2).iloc[-1]==100
    assert rsi(pd.Series([3.,2,1]),2).iloc[-1]==0

def test_streak_equal_and_reversal():
    x=pd.Series([10.,11,12,12,11,10,11])
    np.testing.assert_allclose(streak(x).iloc[1:],[1,2,0,-1,-2,1])

def test_percent_rank_excludes_current_and_ties():
    x=pd.Series([1.,2,2,2,3])
    assert percent_rank(x,3).iloc[3]==pytest.approx(100/3)
    assert percent_rank(x,3).iloc[4]==100
    assert percent_rank(x,3).iloc[:3].isna().all()

def test_connors_hand_example():
    # Price 10,11,10,12: price RSI2=83.3333; streak 1,-1,1 RSI2=50.
    # Current +20% return exceeds preceding +10% and -9.09%: rank=100.
    x=pd.Series([10.,11,10,12])
    assert connors_rsi(x,2,2,2).iloc[-1]==pytest.approx((100*1.25/1.5+50+100)/3)

def test_cumulative_is_sum_not_longer_rsi():
    x=pd.Series([10.,11,10,12,9,13])
    assert cumulative_rsi(x).iloc[-1]==pytest.approx(rsi(x,2).iloc[-2:].sum())
    assert cumulative_rsi(x).iloc[-1]!=rsi(x,4).iloc[-1]

def test_bands_ddof_and_hv():
    x=pd.Series([1.,2,3,4,5,6])
    assert percent_b(x).iloc[4]==pytest.approx((5-(3-np.sqrt(2)))/(2*np.sqrt(2)))
    assert historical_volatility(x,3).iloc[-1]==pytest.approx(np.std(np.log([4/3,5/4,6/5]),ddof=1)*np.sqrt(252))

def test_consecutive_equality():
    assert consecutive(pd.Series([True,True,False,True]),3).sum()==0
    assert consecutive(pd.Series([True,True,True]),3).iloc[-1]

def test_indicator_prefix_does_not_change_with_future_prices():
    from connors.indicators import features
    from connors.data import synthetic
    b=synthetic(['S'],'2020-01-02','2022-12-30')['S']
    original=features(b);changed=b.copy();changed.iloc[-5:,changed.columns.get_loc('close')]*=3
    pd.testing.assert_frame_equal(original.iloc[:-5],features(changed).iloc[:-5])

def test_missing_rsi_restarts_warmup():
    values=rsi(pd.Series([10.,11,10,np.nan,12,13,12]),2)
    assert values.iloc[3:6].isna().all();assert values.iloc[6]==50
