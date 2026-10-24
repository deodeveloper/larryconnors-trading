import pandas as pd
from ..indicators import consecutive,rsi

def signals(kind,b,f,p,aux):
    c=b.close;r=f.rsi2;trend=c>f.sma200;exit=r>65
    if kind=='rsi2':entry=trend&(r<5);exit=c>f.sma5
    elif kind=='cumulative':entry=trend&(r.rolling(2).sum()<p['threshold'])
    elif kind=='double7':entry=trend&c.eq(c.rolling(7).min());exit=c.eq(c.rolling(7).max())
    elif kind=='sp_short':entry=(c<f.sma200)&consecutive(c.diff()>0,4);exit=c<f.sma5
    elif kind=='ten_day':entry=trend&c.eq(c.rolling(10).min())&(b.volume.shift().rolling(100).mean()>=250000)&(c>5);exit=pd.Series(False,index=b.index)
    elif kind=='overnight':entry=pd.Series(True,index=b.index);exit=pd.Series(False,index=b.index)
    elif kind in ('vix','trin'):
        if aux is None:raise ValueError(f'SKIPPED: {kind} requires explicit auxiliary CSV, not supplied by Alpaca stock bars')
        a=aux.reindex(b.index)
        if a.close.isna().any():raise ValueError('Auxiliary series missing sessions: never forward-filled')
        if kind=='vix':entry=trend&(rsi(a.close,2)>90)&(a.open>a.close.shift())&(r<30)
        else:entry=trend&(r<50)&consecutive(a.close>1,3)
    else:raise ValueError(kind)
    return entry,exit
