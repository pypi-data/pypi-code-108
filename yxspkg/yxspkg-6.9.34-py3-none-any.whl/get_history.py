

#该模块是用来从网上获取股票数据，并在本地建立数据库的
import tushare as ts 
import sqlite3
import StockDataAPI as sda
import time
import sys
import asyncio
import signal
import re
import pandas as pd
from time import strftime,strptime,mktime,localtime

def DaysToDate(x):
    return strftime('%Y-%m-%d',localtime((x-719163)*86400))
def DateToWeekdays(date):
    return (strptime(date, '%Y-%m-%d')[6]+1)%7
def DateToDays(x):
    return int((mktime(strptime(x,'%Y-%m-%d'))+28800)/86400+719163)

class mydb:
    def __init__(self,conn):
        self.conn=sqlite3.connect(conn,check_same_thread=False)
        self.cur=self.conn.cursor()
        self.rows = 0
        self.is_auto_commit=False
    def enable_auto_commit(self,n=2000):
        self.is_auto_commit=True
        self.max_rows_commit=n

    def __del__(self):

        self.commit()
        self.cur.close()
        self.conn.close()
        print('sqlite3 has been closed')

    def dict_to_table(self,dic,table):
        a=[]
        for key,value in dic.items():
            if isinstance(value,int):
                stype = 'int'
            elif isinstance(value,float):
                stype = 'double'
            else:
                stype = 'varchar({0})'.format(len(str(value))+2)
            a.append('{0} {1},'.format(str(key),stype))
        content = ''.join(a)
        s='create table {table}({content})'.format(table = table,content=content[:-1])
        self.cur.execute(s)
    def table_exists(self,table):

        result = self.cur.execute("select * from sqlite_master where name='{name}' ".format(name=table)).fetchall()
        if result:
            return True
        else:
            return False
    def commit(self):
        self.conn.commit()
        print('commit')
    def to_sql(self,table,data):
        s = 'INSERT INTO {} VALUES (?,?,?,?,?,?)'.format(table)
        self.cur.executemany(s,data.values)
        if self.is_auto_commit:
            self.rows+=data.shape[0]
            if self.rows>self.max_rows_commit:
                self.commit()
                self.rows=0
    def select(self,table=None,columns=('*',),where='1=1',return_dict = False):
        c=','.join(columns)
        s='select %s from %s where %s;' % (c,table,where)
        try:
            c=self.cur.execute(s)
        except Exception as err:
            print(s,err)
            return []
        c=self.cur.fetchall()
        if return_dict:
            c=[dict(zip(columns,i)) for i in c]
        return c
class myStockDB(mydb):

    def establish_table(self,tname):
        s='''CREATE TABLE {table_name} (
            date date,
            open decimal(10,2),
            close decimal(10,2),
            high decimal(10,2),
            low decimal(10,2),
            volume int,
            PRIMARY KEY (date))
            '''.format(table_name = tname)
        self.cur.execute(s)
    def update(self,ID):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sem = asyncio.Semaphore(1)
        loop.run_until_complete(self.update_async(ID,sem))
        loop.close()
    async def update_async(self,ID,sem):
        async with sem:
            table_name = 'T_'+ re.sub('[^a-zA-z0-9]','_',ID)
            not_table = False
            if not self.table_exists(table_name):
                not_table = True
            if not_table:
                date1 = (1969,1,1)
            else:
                date = self.cur.execute('select date from {table} order by date desc limit 1;'.format(table = table_name)).fetchall()
                if not date:
                    date1 = (1809,1,1)
                else:
                    days = DateToDays(date[0][0])+1
                    date1 = DaysToDate(days)
                    date1 = [int(i) for i in date1.split('-')]
            date2 = time.localtime()
            date2 = (date2.tm_year,date2.tm_mon,date2.tm_mday)
            if date1 == date2:
                print(ID,'无需更新')
                return 0
            loop = asyncio.get_event_loop()
            fu = loop.run_in_executor(None,sda.GetHistoryData,ID,date1,date2)
            f = await fu
            if f.empty:
                print(ID,'无需更新','empty')
                return 0
            if not_table:
                self.establish_table(table_name)
            self.to_sql(table_name,f)
            print(ID,'更新从{}到{}'.format(f['date'].iloc[0],f['date'].iloc[-1]))
            return f.shape[0]

    def update_all(self):
        self.enable_auto_commit()
        def exit_update(sig,fra):
            if sys.platform.startswith('win'):
                if sig == 2:
                    self.commit()
                    print('保存完毕')
                    sys.exit(0)
        signal.signal(signal.SIGINT,exit_update)
        async def run():
            l = sda.GetStockID_China()
            sem = asyncio.Semaphore(1)
            
            tasks = [self.update_async(i,sem) for i in l]
            await asyncio.wait(tasks)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())
        loop.close()
        self.commit()
    def update_all_foreign(self):
        self.enable_auto_commit()
        l = sda.GetStockID_Foreign()
        for i in l:
            if not i.isalpha():
                continue 
            if i<'DXC':continue
            print(i)
            table_name = 'T_'+ re.sub('[^a-zA-z0-9]','_',i)
            if not self.table_exists(table_name):
                print(i,'without table')
                continue
            data = pd.read_sql('select * from {}'.format(table_name),self.conn)
            if data.empty:
                date1 = '2017-06-02'
                bdate = None
            else:
                date1 = min(data['date'])
                bdate = max(data['date'])
            if  date1<'2017-02-02':
                print(i,'data is enough',date1)
                continue
            pd_data = sda.GetHistoryData(i,(2016,1,1),(2016,1,9))
            if pd_data.empty:
                print(i,'data is empty')
                continue
            date2 = min(pd_data['date'])
            if date2 < date1:
                print('删除数据',table_name)
                mdate = max(pd_data['date'])
                self.cur.execute('delete from {} where 1=1'.format(table_name))
                self.to_sql(table_name,pd_data)
                print(date2,mdate)
                time.sleep(30)
    def test(self):
        t = self.cur.execute("select * from sqlite_master").fetchall()
        for i in t:
            if i[0]=='table':
                s = i[1][2:]
                if s.isalpha():
                    print(s)

if __name__=='__main__':
    from IPython import embed
    t = myStockDB('stock_data.sqlite3')
    t.test()