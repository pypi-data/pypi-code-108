#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   update.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/10/18 16:30     douly      1.0         update
"""
# import lib
import sys
import pyodbc
from datetime import datetime, timedelta
from operator import and_

from sqlalchemy import create_engine, Column, String, DateTime, Float

from tzx_easy_py.tools.database_tool import model_base, get_session


class HuNanOraclePptn(model_base):  # 原始数据表
	__tablename__ = 'ST_PPTN_R'
	STCD = Column('STCD', String(50), primary_key=True, nullable=False)
	TM = Column('TM', DateTime, primary_key=True, nullable=False)
	DRP = Column('DRP', Float)
	INTV = Column('INTV', Float)
	PDR = Column('PDR', Float)
	DYP = Column('DYP', Float)
	WTH = Column('WTH', String(50))


delta = timedelta(days=5)
start_time = datetime(year=2021, month=1, day=1, hour=0, minute=0)

now = datetime.now()


while start_time < now:
	end_time = start_time + delta
	# oracle_session = get_session('oracle://rwdb_hn:rwdb_hn@192.168.0.71:1521/orcl')
	oracle_session = get_session('oracle://hyits:hyits@10.43.15.4:1521/hnfxorcl')
	result = oracle_session.query(HuNanOraclePptn).filter(and_(HuNanOraclePptn.TM > start_time, HuNanOraclePptn.TM <= end_time)).all()
	print(len(result))

	if len(result) <= 0:
		# print('Finish.', start_time)
		continue

	insert_data = list()
	for r in result:
		insert_data.append(HuNanOraclePptn(STCD=r.STCD, TM=r.TM, DRP=r.DRP, INTV=r.INTV, PDR=r.PDR, DYP=r.DYP, WTH=r.WTH))

	mssql_session = get_session('mssql+pyodbc://sa:3EDC9ijn~@10.43.1.206/hyits?driver=sql+server')
	# mssql_session = get_session('mssql+pyodbc://sa:123456@.\\dly/foredata?driver=sql+server')
	mssql_session.add_all(insert_data)
	mssql_session.commit()
	oracle_session.close()
	mssql_session.close()
	print(start_time)
	start_time = end_time

print('End')
sys.exit(0)
