#!/usr/bin/env python3
import MySQLdb as _pl
__version__='1.1.1'
class mydb(object):
    def __init__(self,user,passwd,host='127.0.0.1',db=None,port=3306):
        self.conn=_pl.connect(host=host,user=user,passwd=passwd,db=db,port=port,charset='utf8')
        self.cur=self.conn.cursor()
        self.conn.autocommit(1)
        self.db=db
    def select(self,table,columns=('*',),where='1=1'):
        c=','.join(columns)
        s='select %s from %s where %s;' % (c,table,where)
        try:
            c=self.cur.execute(s)
        except Exception as err:
            print(s,err)
            return False
        c=self.cur.fetchall()
        return c
    def insertmany(self,table,dl):
        a=[]
        dargvs=dl[0]
        t=','.join(['`'+i+'`' for i in dargvs.keys()])
        for dargvs in dl:
            v=['"'+i+'"' if isinstance(i,str) else str(i) for i in dargvs.values()]
            v=','.join(v)
            v='('+v+')'
            a.append(v)
        a=','.join(a)
        s='insert into '+table+'('+t+') values '+a+';'
        try:
            self.cur.execute(s)
        except:
            return False
        return None
    def insert(self,table,**dargvs):
        t=','.join(['`'+i+'`' for i in dargvs.keys()])
        v=['"'+i+'"' if isinstance(i,str) else str(i) for i in dargvs.values()]
        v=','.join(v)
        v='('+v+')'
        s='insert into '+table+'('+t+') values'+v
        try:
            self.cur.execute(s)
        except:
            return False
        return None
    def execute(self,s):
        try:
            c=self.cur.execute(s)
        except:
            print('Execute wrong sql :',s)
            return False
        c=self.cur.fetchall()
        return c
    def delete(self,table,where):
        self.cur.execute('delete from '+table+' where '+where)
    def update(self,table,where,**kargs):
        s=''
        for i,j in kargs.items():
            s+='`{0}`="{1}",'.format(i,j)
        s='update {table} set {com} where {where}'.format(table=table,com=s[:-1],where=where)
        c=self.cur.execute(s)
        return c
    def CreateTable(self,table,content,coding='ENGINE=InnoDB DEFAULT CHARSET=utf8'):
        self.cur.execute('CREATE TABLE `'+table+'` '+content+' '+coding)
    def AddColumns(self,table,**kargs):
        for key,value in kargs.items():
            self.cur.execute('alter table `'+table+'` add column `'+key+'` '+value)
    def DropColumns(self,table,*targs):
        for i in targs:
            self.cur.execute('alter table `'+table+'` drop column `'+i+'`')
    def DropTable(self,table):
        self.cur.execute('DROP TABLE `%s`;' % (table,))
    def QueryRom(self,db,table=None):
        ''' SELECT sum(DATA_LENGTH)+sum(INDEX_LENGTH) FROM information_schema.TAbles where TABLE_SCHEMA='stock';'''
        x=self.cur.execute("SELECT sum(DATA_LENGTH)+sum(INDEX_LENGTH) FROM information_schema.TAbles where TABLE_SCHEMA='%s';" % (db,))
        return self.cur.fetchall()[0][0]/(1024**3)
    def __del__(self):
        self.cur.close()
        self.conn.close()