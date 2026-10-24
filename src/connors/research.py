"""Chronological partitions; every attempted configuration is journaled."""
import json,hashlib
from pathlib import Path
import pandas as pd

def partition(cfg,split):
    import copy
    c=copy.deepcopy(cfg);r=c.get('research',{})
    ranges=r.get('splits',{})
    if not ranges:raise ValueError('Define chronological train/validation/test ranges')
    previous=None
    for key in ['train','validation','test']:
        a,b=map(pd.Timestamp,ranges[key])
        if a>b or previous is not None and a<=previous:raise ValueError('Splits must be ordered and non-overlapping')
        previous=b
    c['data']['start'],c['data']['end']=ranges[split];c['research']['selected_split']=split
    return c

def record(cfg,path,status):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(cfg,sort_keys=True,default=str);key=hashlib.sha256(raw.encode()).hexdigest()
    with p.open('a') as f:f.write(json.dumps(dict(config_hash=key,status=status,config=cfg))+'\n')
