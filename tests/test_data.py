import pandas as pd
import pytest
from connors.data import fetch,validate,synthetic,sessions,warmup_start
from connors.research import partition

class Response:
    status_code=200;headers={}
    def __init__(self,body):self.body=body
    def json(self):return self.body
    def raise_for_status(self):pass
class Session:
    def __init__(self,pages):self.pages=pages;self.calls=[]
    def get(self,url,**kwargs):self.calls.append(dict(kwargs['params']));return Response(self.pages.pop(0))

def test_pagination_cache_and_symbol_order(tmp_path,monkeypatch):
    monkeypatch.setenv('APCA_API_KEY_ID','FAKE_TEST_KEY');monkeypatch.setenv('APCA_API_SECRET_KEY','FAKE_TEST_SECRET')
    bar={'t':'2022-01-03T05:00:00Z','o':100,'h':101,'l':99,'c':100,'v':1000}
    fake=Session([{'bars':{'A':[bar]},'next_page_token':'two'},{'bars':{'B':[bar]},'next_page_token':None}])
    cfg={'data':{'symbols':['A','B'],'start':'2022-01-03','end':'2022-01-03','cache':str(tmp_path)}}
    bars=fetch(cfg,fake);assert len(fake.calls)==2;assert fake.calls[1]['page_token']=='two'
    assert list(bars)==['A','B'];assert bars['A'].index[0]==pd.Timestamp('2022-01-03')
    assert len(fetch(cfg,Session([]))['A'])==1

def test_calendar_missing_duplicates_no_weekend_fill():
    b=synthetic(['S'],'2022-01-03','2022-01-10')['S']
    assert len(b)==6;assert not validate(b)['missing_sessions']
    assert len(validate(b.drop(b.index[2]))['missing_sessions'])==1
    with pytest.raises(ValueError,match='Duplicate'):validate(pd.concat([b,b.iloc[:1]]))
    assert len(sessions(warmup_start('2022-01-03'), '2021-12-31'))>=600

def test_chronological_partition():
    cfg={'data':{},'research':{'splits':{'train':['2020-01-01','2020-12-31'],'validation':['2021-01-01','2021-12-31'],'test':['2022-01-01','2022-12-31']}}}
    assert partition(cfg,'test')['data']['start']=='2022-01-01'
    cfg['research']['splits']['test'][0]='2021-01-01'
    with pytest.raises(ValueError):partition(cfg,'test')

def test_intraday_early_close_and_missing_minutes():
    from connors.data import aggregate_sessions
    # Day after Thanksgiving is a 13:00 New York close.
    idx=pd.date_range('2023-11-24 09:30',periods=210,freq='min',tz='America/New_York')
    b=pd.DataFrame({'open':100.,'high':101.,'low':99.,'close':100.,'volume':10},index=idx)
    daily=aggregate_sessions(b)
    assert len(daily)==1;assert daily.volume.iloc[0]==2100
    with pytest.raises(ValueError,match='Incomplete'):aggregate_sessions(b.drop(idx[5]))
