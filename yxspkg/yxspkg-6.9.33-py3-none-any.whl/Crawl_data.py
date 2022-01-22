import sqlite3 
import tushare as ts
import pandas as pd
import time
import datetime
from pathlib import Path
import json
tables_cache = set()
log_info = {'start_time':None,'end_time':None}
def is_table(cursor,table_name):
    global tables_cache
    if not tables_cache:
        cmd = f"SELECT name FROM sqlite_master where type='table'"
        t = [i[0] for i in cursor.execute(cmd)]
        tables_cache.update(t)
    return table_name in tables_cache
def get_log(db,cursor):
    table_name = 'log_info'
    if not is_table(cursor,'log_info'):
        cmd = f'''CREATE TABLE {table_name}
        (start_time    TEXT PRIMARY KEY    NOT NULL,
         end_time      TEXT NOT NULL);'''
        cursor.execute(cmd)
        db.commit()
    cmd = f"select * from {table_name} order by start_time desc limit 1"
    rr = list(cursor.execute(cmd))
    return rr
def set_log(db,cursor):
    insert_dict(db,cursor,log_info,'log_info')
def insert_dict(db,cursor,d,table_name):
    ks = ','.join(["'{"+i+"}'" for i in d.keys()])
    fs1 = f"insert INTO {table_name} (start_time,end_time) VALUES ({ks})".format(**d)
    cursor.execute(fs1)
    db.commit()
def insert_to_table(cursor,table_name,df):
    # table必然存在 且df的数据都是最新的不会重复
    keys = df.keys()
    ks = ','.join(keys)
    fs1 = f"insert INTO stock_basic ({ks}) "
    nk = ','.join(["'{}'"]*len(keys))
    fs2 = f"VALUES ({nk})"
    for _,k in df.iterrows():
        t = [k[v] for v in keys]
        s = fs2.format(*t)
        cursor.execute(fs1+s)
def convert2table_name(ts_code):
    return 'tb_'+ts_code.replace('.','_')
def update_stock_daily(db,cursor,pro,ts_code):
    global tables_cache
    keys = 'trade_date','open','high','low','close','vol','amount'
    table_name = convert2table_name(ts_code)
    if not is_table(cursor,table_name):
        df = pro.daily(ts_code=ts_code)
        cmd = f'''CREATE TABLE {table_name}
        (trade_date    TEXT     PRIMARY KEY     NOT NULL,
        open           real     NOT NULL,
        high           real     NOT NULL,
        low            real     NOT NULL,
        close          real     NOT NULL,
        vol            real     NOT NULL,
        amount         real     NOT NULL);'''
        cursor.execute(cmd)
        db.commit()
        ks = ','.join(keys)
        fs1 = f"insert INTO {table_name} ({ks}) "
        for _,k in df.iterrows():
            t = [k[v] for v in keys]
            s = f"VALUES ('{t[0]}',{t[1]},{t[2]},{t[3]},{t[4]},{t[5]},{t[6]})"
            cursor.execute(fs1+s)
        db.commit()
        tables_cache.update([table_name])
        return True 
    else: 
        return False
def get_info(cursor,ts_code):
    table_name = convert2table_name(ts_code)
    cmd = f"select trade_date from {table_name} order by trade_date desc limit 1"
    rr = list(cursor.execute(cmd))
    if not rr:
        return None 
    else:
        return rr[0][0]


def update_stock_basic(db,cursor,pro):
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    if not is_table(cursor,'stock_basic'):
        cursor.execute('''CREATE TABLE stock_basic
        (ts_code       TEXT    PRIMARY KEY     NOT NULL,
        symbol         TEXT    NOT NULL,
        name           TEXT     NOT NULL,
        area           TEXT     NOT NULL,
        industry       TEXT     NOT NULL,
        list_date      TEXT     NOT NULL);''')
        db.commit()
    ts_code_list = cursor.execute('''SELECT ts_code from stock_basic ''')
    ts_code_list = [i[0] for i in ts_code_list]
    dfnew = []
    for _,k in data.iterrows():
        if k['ts_code'] not in ts_code_list:
            dfnew.append(k)
    dfnew = pd.DataFrame(dfnew)
    if dfnew.size>0:
        insert_to_table(cursor,'stock_basic',dfnew)
        db.commit()
def update_daily(db,cursor,pro):
    pool = ['000001.SZ', '000002.SZ', '000004.SZ', '000005.SZ']
    max_date = '19990101'
    for ts_code in pool:
        t = get_info(cursor,ts_code)
        if t > max_date:
            max_date = t 
    
    latest = datetime.date(int(max_date[:4]),int(max_date[4:6]),int(max_date[6:8]))
    delta_day = datetime.timedelta(days=1)
    today = datetime.datetime.today().date()
    today_str = str(today).replace('-','')
    update_day = latest

    keys = 'trade_date','open','high','low','close','vol','amount'
    ks = ','.join(keys)

    while True:
        update_day = update_day + delta_day 
        update_day_str = str(update_day).replace('-','')
        if update_day_str > today_str:
            break
        print('update ',update_day_str)
        df = pro.daily(trade_date=update_day_str)
        for _,row in df.iterrows():
            table_name = convert2table_name(row['ts_code'])
            if not is_table(cursor,table_name):
                update_stock_daily(db,cursor,pro,row['ts_code'])
                exit()
            fs1 = f"replace INTO {table_name} ({ks}) "
            t = [row[v] for v in keys]
            s = f"VALUES ('{t[0]}',{t[1]},{t[2]},{t[3]},{t[4]},{t[5]},{t[6]})"
            cursor.execute(fs1+s)
        
        db.commit()
def main():
    token_file = Path.home()/'.yxspkg'/'tushare_rc.json'
    jdata = json.load(open(token_file))
    db = sqlite3.connect(jdata['database'])
    plog = Path(jdata['database']).with_name('crawl.log')
    fp=open(plog,'a+')
    cursor = db.cursor()
    token = jdata['token']
    ts.set_token(token)
    pro = ts.pro_api()
    old_log = get_log(db,cursor)
    log_info['start_time'] = str(datetime.datetime.now())
    fp.write(log_info['start_time']+'\n')
    fp.close()
    wday = datetime.datetime.today().weekday()
    if wday == 0 or True:
        update_stock_basic(db,cursor,pro)
        ts_code_list = cursor.execute('''SELECT ts_code from stock_basic ''')
        ts_code_list = [i[0] for i in ts_code_list]
        for ii,ts_code in enumerate(ts_code_list):
            print('update ',ts_code,f'{(ii+1)}/{len(ts_code_list)}')
            update_stock_daily(db,cursor,pro,ts_code)
    update_daily(db,cursor,pro)    
    log_info['end_time'] = str(datetime.datetime.now())
    set_log(db,cursor)
if __name__=='__main__':
    main()