import requests
import re
import sqlite3
import os
from pathlib import Path
import sys
import time
def setheaders():
        headers='''
User-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Host: kyfw.12306.cn
Referer: https://kyfw.12306.cn/otn/leftTicket/init
'''
        headers=headers.split('\n')
        d=dict()
        for i in headers:
            n=i.find(':')
            if n ==-1:continue
            d[i[:n].strip()]=i[n+1:].strip()
        return d
session = requests.session()
session.headers.update(setheaders())

if sys.platform.startswith('win'):
    sql_path = Path(os.environ['HOMEPATH']) / '.yxspkg' / 'tickets_12306.sqlite3'
    sql_path = os.environ['HOMEDRIVE'] / sql_path
else:
    sql_path = Path(os.environ['HOME']) / '.yxspkg' / 'tickets_12306.sqlite3'
conn = sqlite3.connect(sql_path)
cur = conn.cursor()
def get_stations(write_file=False):
    # 7@cqn|重庆南|CRW|chongqingnan|cqn|

    try:
        stations = cur.execute('select name,ID,pinyin from stations').fetchall()
    except Exception as e:
        print(e)
        stations = None
    if stations is None:
        try:
            cur.execute('drop table stations')
        except:
            pass
        cur.execute('''CREATE TABLE stations (
            name nvarchar(7),
            ID char(3),
            pinyin varchar(15),
            primary key (ID))''')

        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8968'
        r = requests.get(url,verify=False)
        patter = re.compile('([^\|a-zA-Z]+)\|([A-Z]+)\|([a-z]+)')
        stations = re.findall(patter,r.text)
        s = 'insert into stations values (?,?,?)'
        cur.executemany(s,stations)
        conn.commit()
    # pinyin2ID = {p:i for n,i,p in stations}
    ID2name = {i:n for n,i,p in stations}
    name2ID = {n:i for n,i,p in stations}
    return name2ID,ID2name
    

name2ID,ID2name = get_stations()



def get_trains(from_station,to_station,date,simple_info=False):
    # 获取 出发站点和目标站点
    from_station = name2ID[from_station] #出发站点
    to_station = name2ID[to_station] # 目的站点
    leave_time = date# 出发时间

    url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date={0}&leftTicketDTO.from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT'.format(
        leave_time,from_station,to_station)# 拼接请求列车信息的Url

    # 获取列车查询结果
    r = session.get(url)
    traindatas = r.json()['data']['result'] # 返回的结果，转化成json格式，取出datas，方便后面解析列车信息用

    # 解析列车信息
    views = TrainCollection(traindatas)
    trains = views.trains()
    if simple_info:
        header = '''车次 出发站 到达站 出发时间 到达时间 历时 日期 高级软卧 商务座 动卧 软卧 硬卧 一等座 二等座 硬座 无座'''.split()
        trains = {k:{i:dd[i] for i in header if dd[i]} for k,dd in trains.items()}
    return trains

def get_train_info(train,train_no = None,from_station=None,to_station=None,date=None):
    #uu = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=67000T838000&from_station_telecode=OTQ&to_station_telecode=GGQ&depart_date=2018-09-20'
    if isinstance(train,str):
        pass
    else:
        train_no, from_station, to_station = train['序号'],name2ID[train['起始站']],name2ID[train['终点站']]
        date = train['日期']
        date = '{}-{}-{}'.format(date[:4],date[4:6],date[6:8])
    url0 = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={train_no}&from_station_telecode={from_station}&to_station_telecode={to_station}&depart_date={date}'
    url = url0.format(train_no=train_no,from_station=from_station,to_station=to_station,date=date) 
    t = session.get(url)
    j = t.json()
    return j['data']['data']
def get_train_all(train,train_no = None,from_station=None,to_station=None,date=None):
    '''
    获取该车在各个区间的所有座位情况
    '''
    ts = get_train_info(train)
    a = []
    if from_station is None:
        from_station = train['出发站']
    if to_station is None:
        to_station = train['到达站']
    train_ID = train['车次']
    if date is None:
        date = train['日期']
        date = '{}-{}-{}'.format(date[:4],date[4:6],date[6:8])
    is_start = False
    for i in range(len(ts)-1):
        name1 = ts[i]['station_name']
        name2 = ts[i+1]['station_name']
        if not is_start:
            if name1 == from_station:
                is_start = True
            else:
                continue 
    
        print(name1, name2, date,'#'*9)
        k = get_trains(name1, name2, date)[train_ID]
        print(k)
        a.append(k)

        start_time = k['出发时间']
        duration = k['历时']
        t1 = int(start_time[:2])*60 + int(start_time[-2:])
        t2 = int(duration[:2])*60 + int(duration[-2:])
        if t1+t2>=24*60:
            t = time.strptime(date,'%Y-%m-%d')
            t = time.mktime(t)+24*3600
            date = time.strftime('%Y-%m-%d',time.localtime(t))

        if name2 == to_station:
            break
    return a
class TrainCollection:
    """
    解析列车信息
    """
    # 显示车次、出发/到达站、 出发/到达时间、历时、一等坐、二等坐、软卧、硬卧、硬座
    header = '''_0_ 状态 序号 车次 起始站 终点站 出发站 到达站 出发时间 到达时间 历时 卖否 _12_ 日期 _14_ _15_
    _16_ _17_ _18_ _19_ _20_ 高级软卧 _22_ 软卧 _24_ _25_ 无座 _27_ 硬卧 硬座 二等座 一等座 商务座 动卧 _34_ _35_ _36_'''.split()
    #软座 其他
    def __init__(self,rows):
        self.rows = rows

    def trains(self):
        result = [dict(zip(self.header, row.split('|'))) for row in self.rows]
        r = [{k:dic[k] for k in dic if not k.startswith('_')} for dic in result]
        d = {i['车次']:i  for i in r}
        for v in d.values():
            for i in ['起始站', '终点站', '出发站', '到达站']:
                v[i]=ID2name[v[i]]  
        return d


if __name__ == '__main__':
    t = get_trains('北京','中卫','2018-09-25')
    print(t)
    info = get_train_info(t['Z21'])
    print(info)
    all_data = get_train_all(t['Z21'])
    print(all_data)