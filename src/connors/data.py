"""Alpaca REST pagination and session-aware validation. Never fills missing prices."""
import hashlib,json,os,time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import exchange_calendars as xc

def credentials():
    keys=['APCA_API_KEY_ID','APCA_API_SECRET_KEY'];values=[]
    for key in keys:
        v=os.environ.get(key)
        if not v:
            try:
                from google.colab import userdata
                v=userdata.get(key)
            except (ImportError,KeyError):pass
        if not v:raise ValueError(f'Missing credential {key}; set environment or Colab Secret')
        values.append(v)
    return dict(zip(['APCA-API-KEY-ID','APCA-API-SECRET-KEY'],values))
def calendar(start,end):return xc.get_calendar('XNYS',start=pd.Timestamp(start)-pd.Timedelta(days=7),end=pd.Timestamp(end)+pd.Timedelta(days=7))
def sessions(start,end):return calendar(start,end).sessions_in_range(start,end).tz_localize(None)
def warmup_start(start,n=600):
    start=pd.Timestamp(start);cal=calendar(start-pd.Timedelta(days=n*2),start)
    past=cal.sessions[cal.sessions.tz_localize(None)<start]
    if len(past)<n:raise ValueError('Insufficient calendar warmup')
    return past[-n].date().isoformat()
def validate(b,start=None,end=None):
    if b.index.has_duplicates:raise ValueError('Duplicate timestamps detected')
    if not b.index.is_monotonic_increasing:raise ValueError('Bars must be sorted')
    cols=['open','high','low','close','volume']
    if b[cols].isna().any().any():raise ValueError('Missing OHLCV values')
    if (b[cols[:4]]<=0).any().any() or (b.volume<0).any():raise ValueError('Invalid price/volume')
    if ((b.high<b[['open','close','low']].max(axis=1))|(b.low>b[['open','close','high']].min(axis=1))).any():raise ValueError('Inconsistent OHLC')
    expected=sessions(start or b.index[0].date(),end or b.index[-1].date())
    missing=expected.difference(b.index);extra=b.index.difference(expected)
    return {'rows':len(b),'missing_sessions':[str(t.date()) for t in missing],'non_sessions':[str(t.date()) for t in extra],'duplicates':0}
def fetch(cfg,session=None):
    d=cfg['data'];start=warmup_start(d['start'],d.get('warmup_sessions',600))
    params=dict(symbols=','.join(d['symbols']),start=start,end=(pd.Timestamp(d['end'])+pd.Timedelta(days=1)).date().isoformat(),timeframe=d.get('timeframe','1Day'),feed=d.get('feed','iex'),adjustment=d.get('adjustment','split'),limit=10000,sort='asc')
    key=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()
    cache=Path(d.get('cache','.cache/alpaca'));cache.mkdir(parents=True,exist_ok=True);file=cache/(key+'.json')
    if file.exists():raw=json.loads(file.read_text())
    else:
        headers=credentials();client=session or requests.Session();raw={s:[] for s in d['symbols']};seen=set()
        while True:
            for attempt in range(5):
                try:
                    response=client.get('https://data.alpaca.markets/v2/stocks/bars',params=params,headers=headers,timeout=45)
                    if response.status_code in [429,500,502,503,504]:
                        if attempt==4:response.raise_for_status()
                        time.sleep(min(float(response.headers.get('Retry-After',2**attempt)),30));continue
                    response.raise_for_status();break
                except (requests.ConnectionError,requests.Timeout):
                    if attempt==4:raise
                    time.sleep(2**attempt)
            page=response.json()
            for s,bars in page.get('bars',{}).items():raw.setdefault(s,[]).extend(bars)
            token=page.get('next_page_token')
            if not token:break
            if token in seen:raise ValueError('Pagination token repeated')
            seen.add(token);params['page_token']=token
        tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(raw));tmp.replace(file)
    result={}
    for symbol in d['symbols']:
        if not raw.get(symbol):raise ValueError(f'No Alpaca bars for {symbol}; unsupported asset/feed/date; no proxy substitution')
        b=pd.DataFrame(raw[symbol]).rename(columns=dict(o='open',h='high',l='low',c='close',v='volume'))
        ts=pd.to_datetime(b.pop('t'),utc=True)
        b.index=pd.DatetimeIndex(ts).tz_convert(d.get('timezone','America/New_York'))
        if b.index.has_duplicates:raise ValueError('Duplicate Alpaca timestamps')
        if params['timeframe'] in ['1Day','1D']:b.index=b.index.tz_localize(None).normalize()
        elif d.get('regular_session',True):
            cal=calendar(start,d['end']);schedule=cal.schedule
            keep=np.zeros(len(b),dtype=bool)
            for _,row in schedule.iterrows():keep|=(b.index>=row['open'])&(b.index<row['close'])
            b=b.loc[keep]
        result[symbol]=b[['open','high','low','close','volume']].sort_index()
    return result

def synthetic(symbols=('SYNTH',),start='2018-01-01',end='2024-12-31'):
    idx=sessions(start,end);n=len(idx);result={}
    for j,s in enumerate(symbols):
        rng=np.random.default_rng(41+j);x=np.arange(n)
        c=100*np.exp(.00035*x+.065*np.sin(x/11)+.018*np.sin(x/2)+rng.normal(0,.004,n))
        o=np.r_[c[0],c[:-1]]*(1+rng.normal(0,.003,n))
        result[s]=pd.DataFrame(dict(open=o,high=np.maximum(c,o)*1.009,low=np.minimum(c,o)*.991,close=c,volume=np.full(n,2000000)),index=idx)
    return result

def load_aux(path):
    if not path:return None
    b=pd.read_csv(path,index_col=0,parse_dates=True);b.index=pd.DatetimeIndex(b.index).tz_localize(None).normalize()
    if b.index.has_duplicates:raise ValueError('Duplicate auxiliary dates')
    return b.sort_index()

def aggregate_sessions(b,timeframe='1Min',timezone='America/New_York'):
    """Strict RTH aggregation; missing interval bars are reported, never fabricated.

    Some feeds omit no-trade minutes. Such inputs fail strict coverage rather than
    silently claiming a complete session. Use daily bars or supply verified data.
    """
    import re
    match=re.fullmatch(r'(\d+)(Min|Hour)',timeframe)
    if not match:raise ValueError('Intraday aggregation accepts nMin or nHour')
    step=pd.Timedelta(minutes=int(match[1])*(60 if match[2]=='Hour' else 1))
    if b.index.tz is None:raise ValueError('Intraday input needs timezone-aware timestamps')
    if b.index.has_duplicates:raise ValueError('Duplicate intraday timestamps')
    local=b.index.tz_convert(timezone);start=local.min().date();end=local.max().date()
    cal=calendar(start,end);rows=[];dates=[]
    for day in cal.sessions_in_range(start,end):
        row=cal.schedule.loc[day];opening=row['open'];closing=row['close']
        expected=pd.date_range(opening,closing,freq=step,inclusive='left')
        sub=b.loc[(b.index>=opening)&(b.index<closing)]
        if len(expected.difference(sub.index)) or len(sub.index.difference(expected)):
            raise ValueError(f'Incomplete or misaligned intraday coverage for {day.date()}; no forward fill')
        rows.append(dict(open=sub.open.iloc[0],high=sub.high.max(),low=sub.low.min(),close=sub.close.iloc[-1],volume=sub.volume.sum()));dates.append(day)
    return pd.DataFrame(rows,index=pd.DatetimeIndex(dates).tz_localize(None))
