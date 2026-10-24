import argparse,copy,json
from pathlib import Path
import yaml
from .strategies import catalog,resolve
from .data import fetch,synthetic,validate,load_aux,warmup_start,aggregate_sessions
from .execution import run
from .reporting import export
from .research import record,partition

def _execute(cfg,output=None):
    spec,p=resolve(cfg['strategy'],cfg.get('parameters'),cfg.get('allow_experimental',False))
    d=cfg['data']
    intraday=d.get('timeframe','1Day') not in ['1Day','1D']
    if intraday and not d.get('aggregate_daily',False):raise ValueError('Book rules are daily; set aggregate_daily to reconstruct complete regular sessions from intraday bars')
    if d.get('adjustment','split') not in ['split','all']:raise ValueError('Raw execution with corporate action cash/share processing is not implemented. Choose split or all adjusted research units.')
    if d.get('warmup_sessions',600)<300:raise ValueError('Require >=300 warmup sessions for nested indicators and 252-day highs; default 600')
    provider=d.get('provider','synthetic')
    if provider=='synthetic':bars=synthetic(d['symbols'],warmup_start(d['start'],d.get('warmup_sessions',600)),d['end'])
    elif provider=='alpaca':bars=fetch(cfg)
    elif provider=='csv':
        import pandas as pd
        bars={s:pd.read_csv(d['csv'][s],index_col=0,parse_dates=True) for s in d['symbols']}
    else:raise ValueError('Unknown provider')
    if intraday:bars={s:aggregate_sessions(b,d['timeframe'],d.get('timezone','America/New_York')) for s,b in bars.items()}
    quality={s:validate(b,warmup_start(d['start'],d.get('warmup_sessions',600)),d['end']) for s,b in bars.items()}
    for s,q in quality.items():
        if q['missing_sessions'] or q['non_sessions']:raise ValueError(f'{s}: missing/non-session bars; inspect coverage instead of filling gaps')
    if spec['id'] in ['buy_fear.vol_panics','buy_fear.vxx_trend'] and provider!='synthetic' and any(s!='VXX' for s in d['symbols']):
        if not d.get('proxy'):raise ValueError('VXX strategy on other symbols requires recorded proxy configuration')
    if spec['id'].startswith('short_term.') and spec['id'].split('.')[1] in ['rsi2','double7','vix','trin','sp_short','overnight'] and provider!='synthetic' and any(s not in (['SPY','QQQ','FXI','EWZ'] if spec['id']=='short_term.double7' else ['SPY']) for s in d['symbols']):
        if not d.get('proxy'):raise ValueError('Market system requires explicit universe/proxy configuration')
    result=run(bars,spec,p,cfg,load_aux(cfg.get('auxiliary_csv')))
    return export(result,output or cfg.get('output','reports/run'),quality)

def execute(cfg,output=None):
    journal=cfg.get('research',{}).get('journal','reports/research.jsonl')
    record(cfg,journal,'started')
    try:
        result=_execute(cfg,output)
    except Exception as err:
        record(cfg,journal,'failed: '+type(err).__name__)
        raise
    record(cfg,journal,'completed')
    return result

def main():
    parser=argparse.ArgumentParser(description='Source-linked daily strategy research')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('list')
    for cmd in ['fetch','run','variants','report']:
        s=sub.add_parser(cmd);s.add_argument('config');s.add_argument('--output');s.add_argument('--split',choices=['train','validation','test'])
    args=parser.parse_args()
    if args.command=='list':
        for r in catalog()['strategies']:print(r['id'],r['status'],r.get('reason',''))
        print('Named variants:',', '.join(catalog()['variants']));return
    cfg=yaml.safe_load(Path(args.config).read_text())
    if args.split:cfg=partition(cfg,args.split)
    if args.command=='fetch':
        bars=fetch(cfg);print({s:len(b) for s,b in bars.items()});return
    variants=cfg.get('variants',[cfg['strategy']]) if args.command=='variants' else [cfg['strategy']]
    if len(variants)>1 and cfg.get('research',{}).get('selected_split')=='test':raise ValueError('No variant sweep on final test split')
    for name in variants:
        c=copy.deepcopy(cfg);c['strategy']=name
        out=Path(args.output or cfg.get('output','reports/run'))
        if len(variants)>1:out=out/name
        journal=cfg.get('research',{}).get('journal','reports/research.jsonl')
        try:
            result=execute(c,out);print(name,json.dumps(result['metrics'],indent=2))
        except ValueError as err:
            if len(variants)==1:raise
            print(name,'SKIPPED:',err)
if __name__=='__main__':main()
