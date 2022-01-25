import time,requests,re
import tushare
import pandas as pd
try:
    import pandas_datareader.data as web
    import pandas_datareader as pdr
except:
    pass
import datetime
import numpy as np
try:
    import quandl
    quandl.ApiConfig.api_key = 'T8xnGQAYzBw5F6vsSYVs'
    quandl.ApiConfig.api_version = '2015-04-09'
except:
    pass

session=requests.Session()
session.headers={'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate',
'DNT': '1',
'Connection': 'keep-alive'}
def GetDataFromSina(stockID,date1=None,date2=None,stockExchange=None):
    if date1 is None:date1=(1700,1,1)
    else:date1=tuple(date1)
    if date2 is None:date2=(2700,12,10)
    else:date2=tuple(date2)
    url='http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/%s.phtml' % (stockID,)
    session.headers['Host']='money.finance.sina.com.cn'
    dataPattern=re.compile(r'(\d\d\d\d-\d\d?-\d\d?)""(\d*\.?\d+)""(\d*\.?\d+)""(\d*\.?\d+)""""(\d*\.?\d+)""""(\d*)""""(\d*)')
    columns=dict(zip(('Date','Open','High','Close','Low','Volume','Value'),range(7)))
    def GetYear():
        p=re.compile(r'<option value="(\d\d\d\d)" ')
        x=session.get(url)
        return p.findall(x.text)
    def GetData(params0):
        x=session.get(url,params=params0)
        d=re.sub(r'[^\.0-9"-]','',x.text)
        return dataPattern.findall(d)
    years=[int(i) for i in GetYear() if int(i)>=date1[0] and int(i)<=date2[0]]
    years.sort()
    if len(years)==0:return None,[]
    if len(years)==1:years*=2
    jidu1,jidu2=int((date1[1]-1)//3)+1,int((date2[1]-1)//3)+1
    year=years[0]
    yearEnd=years[-1]
    a=[]
    while year*10+jidu1<=yearEnd*10+jidu2:
        params={'year':str(year),'jidu':str(jidu1)}
        x=GetData(params)
        a.extend(x)
        jidu1+=1
        if jidu1==5:
            jidu1=1
            year+=1
    if date1 is not None and len(a)>0:
        date1='%4d-%02d-%02d' % date1
        a=[i for i in a if i[0]>=date1]
    if date2 is not None and len(a)>0:
        date2='%4d-%02d-%02d' % date2
        a=[i for i in a if i[0]<=date2]
    k = pd.DataFrame(a,columns = ('date', 'open', 'close', 'high', 'low', 'volume','value'))
    
    k = k.loc[:,('date', 'open', 'close', 'high', 'low', 'volume')]
    m = k.sort_values(by='date')
    return m
def GetDataFromTencent(stockID,date1=None,date2=None,stockExchange='None'):
    url='http://data.gtimg.cn/flashdata/hushen/latest/daily/%s.js?maxage=43201'
    session.headers['Host']='data.gtimg.cn'
    if stockExchange.lower() not in ('ss','sz'):return None,None
    url=url % (stockExchange.lower()+stockID,)
    d=session.get(url)
    d=d.text.replace('\\n\\','00').split('\n')[2:-1]
    d=[i.split() for i in d]
    if date1 is not None and len(d)>0:
        date1=('%4d%02d%02d' % date1)[2:]
        d=[i for i in d if i[0]>=date1]
    if date2 is not None and len(d)>0:
        date2=('%4d%02d%02d' % date2)[2:]
        d=[i for i in d if i[0]<=date2]
    f=lambda x:'19' if x[0]>'7' else '20'
    d=[('%s%s-%s-%s' % (f(i),i[:2],i[2:4],i[4:]), j,k,l,m,n) for i,j,k,l,m,n in d]
    return {'Date':0,'Open':1,'Close':2, 'High':3,'Low':4,'Volume':5},d
def GetDataFromYahoo(stockID,date1=None,date2=None,stockExchange='None'):
    url0='http://table.finance.yahoo.com/table.csv?s=%s'
    session.headers['Host']='table.finance.yahoo.com'
    if stockExchange.lower() in ['sz','ss']:stockID=stockID+'.'+stockExchange
    params=[stockID]
    if date1 is not None:
        url0+='&c=%s&a=%s&b=%s'
        params.extend(date1)
        params[-2]-=1
    if date2 is not None:
        url0+='&f=%s&d=%s&e=%s'
        params.extend(date2)
        params[-2]-=1
    url=url0 % tuple(params)
    r=session.get(url).text.split('\n')
    if r[0].find('Date')==-1:return None,[]

    columns=dict(zip(('Date','Open','High','Low','Close','Volume','AdjClose'),range(7)))

    a = [i.split(',') for i in r[1:-1]]

    return columns,a
def GetDataFromHexun(stockID,date1=(2016,5,2),date2=(2016,10,9)):
    url='http://webstock.quote.hermes.hexun.com/a/kline?code=sse601398&start=20150909150000&number=-10&type=5' % (stockID,)
    session.headers['Host']='money.finance.sina.com.cn'
    dataPattern=re.compile(r'(\d\d\d\d-\d\d?-\d\d?)""(\d*\.?\d+)""(\d*\.?\d+)""(\d*\.?\d+)""""(\d*\.?\d+)""""(\d*)""""(\d*)')
    columns='Date','Open','High','Close','Low','Volume','Value'
    def GetYear():
        p=re.compile(r'<option value="(\d\d\d\d)" ')
        x=session.get(url)
        return p.findall(x.text)
    def GetData(params0):
        x=session.get(url,params=params0)
        d=re.sub(r'[^\.0-9"-]','',x.text)
        return dataPattern.findall(d)
    years=[int(i) for i in GetYear() if int(i)>=date1[0] and int(i)<=date2[0]]
    if len(years)==1:years*=2
    jidu1,jidu2=int((date1[1]-1)//3)+1,int((date2[1]-1)//3)+1
    year=years[0]
    yearEnd=years[-1]
    a=[]
    while year*10+jidu1<=yearEnd*10+jidu2:
        print(year,jidu1)
        params={'year':str(year),'jidu':str(jidu1)}
        x=GetData(params)
        a.extend(x)
        jidu1+=1
        if jidu1==5:
            jidu1=1
            year+=1
    return columns,a
def GetStockID_China():
    m = tushare.get_industry_classified()
    l = list(set(m['code']))
    l.sort()
    return l
def GetStockID_Foreign():
    t = web.get_iex_symbols()
    l = list(t['symbol'])
    l.sort()
    return l
def GetDataFromTushare(stockID,date1=None,date2=None,stockExchange='None'):
    x=tushare.get_k_data(stockID,start = '{0:04d}-{1:02d}-{2:02d}'.format(*date1),end = '{0:04d}-{1:02d}-{2:02d}'.format(*date2))
    if x.empty:
        x = pd.DataFrame(columns=['date', 'open', 'close', 'high', 'low', 'volume'])
    t = x.loc[:,('date', 'open', 'close', 'high', 'low', 'volume')]
    return t
def GetDataFromPandas(stockID,date1=None,date2=None,stockExchange='None'):
    x=pdr.get_data_yahoo(stockID,start = '{0:04d}-{1:02d}-{2:02d}'.format(*date1),end = '{0:04d}-{1:02d}-{2:02d}'.format(*date2))
    if x.empty:
        x = pd.DataFrame(columns=['date', 'open', 'close', 'high', 'low', 'volume'])
    else:
        x['date'] = x.index.to_native_types()
        t = x[['date', 'Open', 'Close', 'High', 'Low', 'Volume']]
        t.rename(columns = str.lower,inplace = True)
        t.index = range(len(t))
    return t
def GetDataFromForeign(stockID,date1=None,date2=None,stockExchange='None'):
    #尝试quandl
    start,end = datetime.datetime(*date1),datetime.datetime(*date2)
    start_f,end_f = start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d')
    try:
        t = quandl.get_table('WIKI/PRICES', qopts = { 'columns': ['date','open', 'close','high','low','volume'] }, ticker = [stockID,])
        t['volume'] = t['volume'].astype('int')
        t['date'] = t['date'].astype('str')
        return t
    except Exception as e:
        print(stockID,'quandl false',e)
        pass
    #尝试robinhood
    try:
        t = web.get_data_robinhood(stockID,start,end)
        t['date'] = t.index.to_frame()['begins_at'].astype(str)
        t = t.loc[np.logical_and(t['date']>=start_f,t['date']<=end_f),('date','open_price','close_price','high_price','low_price','volume')]
        t.rename(columns={'open_price':'open','close_price':'close','high_price':'high','low_price':'low'},inplace=True)
        return t
    except:
        print(stockID,'robinhood false')
        pass
    return pd.DataFrame(columns=['date', 'open', 'close', 'high', 'low', 'volume'])
def GetHistoryData(stockID,date1=None,date2=None,stockExchange='None',source='Sina'):
    if date2 is None:
        d = datetime.datetime.today()
        date2 = (d.year,d.month,d.day)
    if date1 is None:
        date1 = (2012,1,1)
    if stockID.isdigit() and len(stockID)==6:
        return GetDataFromTushare(stockID,date1,date2)
    else:
        return GetDataFromPandas(stockID,date1,date2)
def GetRealTimeData(stockID,stockExchange='None'):
    label={'ss':'sh','sz':'sz','sh':'sh'}
    key=label.get(stockExchange.lower())
    if key == None:return False
    url='http://hq.sinajs.cn/list=%s%s' % (key,stockID)
    s=requests.get(url).text
    s=s[s.find('"')+1:].split(',')
    try:
        d={'ID':stockID,'Date':s[-3],'Open':float(s[1]),'Current':float(s[3]),'High':float(s[4]),'Low':float(s[5]),'Close':float(s[3]),'Volume':-1,'ChineseName':s[0],'Time':s[-2]}
    except:
        d = None
    return d
if __name__=='__main__':
    t = GetRealTimeData('002013','sz')
    print(t)