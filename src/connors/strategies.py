import json
from importlib.resources import files
from . import indicators
from .hpe.strategy import signals as hpe
from .short_term.strategy import signals as short_term
from .buy_fear.strategy import signals as buy_fear

def catalog():return json.loads(files('connors').joinpath('catalog.json').read_text())
def resolve(name,overrides=None,allow_experimental=False):
    cat=catalog();v=cat['variants'].get(name,{'strategy':name,'parameters':{}})
    spec=next((r for r in cat['strategies'] if r['id']==v['strategy']),None)
    if spec is None:raise ValueError('Unknown strategy '+name)
    if spec['status']=='blocked':raise ValueError('BLOCKED: '+spec['reason'])
    if spec['status']=='experimental' and not allow_experimental:raise ValueError('Requires allow_experimental: '+spec['reason'])
    p={**spec['parameters'],**v['parameters'],**(overrides or {})}
    allowed=set(spec['parameters']) | {'aggressive','volume_filter','equal_units'}
    unknown=set(overrides or {})-allowed
    if unknown:raise ValueError('Unsupported strategy parameters: '+', '.join(sorted(unknown)))
    if spec['id']=='hpe.r3.long' or spec['id']=='hpe.r3.short':
        if p.get('r3_interpretation') not in ['first_declining_reading','preceding_reading']:raise ValueError('Invalid R3 interpretation')
    return spec,p

def generate(spec,b,p,aux=None):
    f=indicators.features(b);book,kind,*_=spec['id'].split('.');d=1 if spec['direction']=='long' else -1
    if kind=='percent_b':f['b']=indicators.percent_b(b.close,p.get('length',5),p.get('std',1),p.get('ddof',0))
    if book=='hpe':en,ex=hpe(kind,b,f,p,d)
    elif book=='short_term':en,ex=short_term(kind,b,f,p,aux)
    else:en,ex=buy_fear(kind,b,f,p)
    return f,en.fillna(False),ex.fillna(False)

def stages(spec,p):
    kind=spec['id'].split('.')[1]
    if kind=='tps':return [.1,.2,.3,.4],False
    if kind=='vol_panics':return p['stages'],p.get('equal_units',False)
    if kind in ['powerzones','rsi2_scale'] or p.get('aggressive'):return [.5,.5],True
    return [1.0],False

def add_allowed(spec,p,b,f,i,last,first):
    kind=spec['id'].split('.')[1];d=1 if spec['direction']=='long' else -1;c=b.close.iloc[i]
    worse=(c-last)*d<0
    if kind=='tps':return worse and ((c>=f.sma200.iloc[i]) if d==1 else (c<=f.sma200.iloc[i]))
    if kind=='vol_panics':return c>(first if p.get('equal_units') else last)
    if kind in ['rsi4','powerzones']:return (f.rsi4.iloc[i]<p['add']) if d==1 else (f.rsi4.iloc[i]>p['add'])
    if kind=='rsi2_scale':return (f.rsi2.iloc[i]<p['add']) if d==1 else (f.rsi2.iloc[i]>p['add'])
    if kind=='percent_b':return f.b.iloc[i]<.2 if d==1 else f.b.iloc[i]>.8
    return (c-first)*d<0
