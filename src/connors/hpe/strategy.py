from ..indicators import consecutive

def signals(kind,b,f,p,d):
    c=b.close;r=f.rsi2;r4=f.rsi4;long=d==1
    trend=c.gt(f.sma200) if long else c.lt(f.sma200)
    low=c.lt(f.sma5) if long else c.gt(f.sma5)
    exit=c.gt(f.sma5) if long else c.lt(f.sma5)
    cmp=lambda x,k:x.lt(k) if long else x.gt(k)
    if kind=='high_low':
        step=(b.high.diff().lt(0)&b.low.diff().lt(0)) if long else (b.high.diff().gt(0)&b.low.diff().gt(0))
        entry=trend&low&consecutive(step,3)
    elif kind=='multiple_days':
        step=c.diff().lt(0) if long else c.diff().gt(0)
        entry=trend&low&(step.rolling(p.get('window',5)).sum()>=p.get('count',4))
    elif kind=='rsi4':
        entry=trend&cmp(r4,p['entry']);exit=r4.gt(p['exit']) if long else r4.lt(p['exit'])
    elif kind=='rsi2_scale':entry=trend&cmp(r,p['entry'])
    elif kind=='percent_b':
        entry=trend&consecutive(cmp(f.b,.2 if long else .8),3)
        exit=f.b.gt(.8) if long else f.b.lt(.2)
    elif kind=='r3':
        offset=2 if p['r3_interpretation']=='first_declining_reading' else 3
        entry=trend&consecutive(cmp(r.diff(),0),3)&cmp(r.shift(offset),60 if long else 40)&cmp(r,10 if long else 90)
        exit=r.gt(70) if long else r.lt(30)
    elif kind=='tps':
        entry=trend&consecutive(cmp(r,25 if long else 75),2)
        if p.get('volume_filter'):entry &= b.volume.shift().rolling(20).mean().ge(250000)
        exit=r.gt(70) if long else r.lt(30)
    else:raise ValueError(kind)
    return entry,exit
