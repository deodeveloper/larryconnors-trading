def signals(kind,b,f,p):
    c=b.close
    if kind=='powerzones':entry=(c>f.sma200)&(f.rsi4<p['entry']);exit=f.rsi4>p['exit']
    elif kind=='crash':entry=(c>5)&(b.volume.rolling(21).mean()>=1000000)&(f.hv>=p['hv_min'])&(f.crsi>=90);exit=f.crsi<p['exit']
    elif kind=='new_highs':
        high=b.high.eq(b.high.rolling(252).max())
        entry=(c>5)&(b.volume.rolling(21).mean()>1000000)&high.rolling(20).max().eq(1)&(f.crsi<15)
        exit=f.crsi>70
    elif kind=='vol_panics':entry=(c>f.sma5)&(f.rsi4>70);exit=(c<f.sma5) if p['exit_kind']=='sma' else (f.rsi4<20)
    elif kind=='vxx_trend':
        fast=f[p['ma']+'10'];slow=f[p['ma']+'30']
        entry=(fast<slow)&(fast.shift()>=slow.shift());exit=(fast>slow)&(fast.shift()<=slow.shift())
    else:raise ValueError('Blocked strategy: '+kind)
    return entry,exit
