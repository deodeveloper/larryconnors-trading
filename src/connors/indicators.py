"""Explicit indicator conventions; no optional TA-Lib dispatch."""
import numpy as np
import pandas as pd
import pandas_ta_classic as ta

def sma(x,n):
    return ta.sma(x,length=n,talib=False)
def ema(x,n):
    return ta.ema(x,length=n,talib=False,sma=True,adjust=False)
def rsi(x,n=2):
    """pandas-ta-classic 0.8.32 SMA-seeded Wilder RSI; flat seed => 50.

    Missing observations restart the warmup. TA-Lib dispatch is disabled.
    """
    out=pd.Series(np.nan,index=x.index)
    valid=x.notna();groups=(~valid).cumsum()
    for _,part in x[valid].groupby(groups[valid]):
        if len(part)<=n:continue
        values=ta.rsi(part,length=n,talib=False)
        values.iloc[n:]=values.iloc[n:].fillna(50.)
        out.loc[part.index]=values
    return out
def streak(x):
    out=pd.Series(np.nan,index=x.index);v=0
    for i in range(1,len(x)):
        if pd.isna(x.iloc[i]) or pd.isna(x.iloc[i-1]):v=0;continue
        d=x.iloc[i]-x.iloc[i-1]
        v=(max(v,0)+1) if d>0 else ((min(v,0)-1) if d<0 else 0)
        out.iloc[i]=v
    return out

def percent_rank(x,n=100):
    """Current return vs preceding n returns; strictly less; ties count zero."""
    return x.rolling(n+1,min_periods=n+1).apply(lambda a:100*np.sum(a[:-1]<a[-1])/n,raw=True)
def connors_rsi(x,price_n=3,streak_n=2,rank_n=100):
    return (rsi(x,price_n)+rsi(streak(x),streak_n)+percent_rank(x.pct_change(fill_method=None),rank_n))/3

def percent_b(x,n=5,std=1,ddof=0):
    bands=ta.bbands(x,length=n,std=float(std),ddof=ddof,talib=False)
    lower=bands.iloc[:,0];upper=bands.iloc[:,2]
    return (x-lower)/(upper-lower).replace(0,np.nan)
def cumulative_rsi(x,rsi_n=2,sum_n=2):return rsi(x,rsi_n).rolling(sum_n).sum()
def historical_volatility(x,n=100,annualization=252):
    """Sample standard deviation of log daily returns, annualized; decimal units."""
    return np.log(x/x.shift()).rolling(n).std(ddof=1)*np.sqrt(annualization)
def consecutive(condition,n):return condition.fillna(False).rolling(n).sum().eq(n)
def features(b):
    x=b.close
    f=pd.DataFrame(index=b.index)
    for n in (5,10,30,200):f[f'sma{n}']=sma(x,n)
    for n in (10,30):f[f'ema{n}']=ema(x,n)
    for n in (2,4):f[f'rsi{n}']=rsi(x,n)
    f['crsi']=connors_rsi(x);f['b']=percent_b(x);f['hv']=historical_volatility(x)
    return f
