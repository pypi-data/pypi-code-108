#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   fore_rain_data_convert.py
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/10/11 13:14     douly      1.0         fore_rain_data
"""
import sys
import time

import toml
import argparse
from datetime import datetime, timedelta
# import lib
from time import sleep
from threading import Thread

import pyodbc

from sqlalchemy import Column, Integer, Float, String, Text, BigInteger, DateTime, create_engine, func, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from com.tzx.tools.clock_tool import to_standard_hour, time_from_str
from com.tzx.tools.database_tool import get_session

class GribWeatherFore(model_base):
	__tablename__ = "tb_gribwf"
	id = Column("id", Integer, nullable=False)
	filename = Column("filename", String(512), primary_key=True)
	wfsrc = Column("wfsrc", String(16))
	area = Column("area", String(16))
	facname = Column("facname", String(32))
	wfdatetime = Column("wfdatetime", BigInteger, primary_key=True)
	wfinterval = Column("wfinterval", Integer)
	wfhours = Column("wfhours", Integer)
	wfhour = Column("wfhour", Integer, primary_key=True)
	upperleft = Column("upperleft", String(50), nullable=False)
	lowerright = Column("lowerright", String(50), nullable=False)
	width = Column("width", Integer, nullable=False)
	height = Column("height", Integer, nullable=False)
	stepx = Column("stepx", Float, nullable=False)
	stepy = Column("stepy", Float, nullable=False)
	data = Column("data", Text, nullable=False)
	data1 = Column("data1", Text, nullable=False)
	status = Column("status", Integer, nullable=False)
	score = Column("score", Text, nullable=False)
	scoretime = Column("scoretime", String(50), nullable=False)
	score1 = Column("score1", Text, nullable=False)
	score2 = Column("score2", Text, nullable=False)
	datatype = Column("datatype", Integer, nullable=False)
	data3 = Column("data3", Text, nullable=False)


class ForeRainPoint(model_base):  # 原始数据表
	__tablename__ = 'ForeRainPoint_B'
	PID = Column("PID", Integer, primary_key=True, autoincrement=True)
	LGTD = Column("LGTD", Float)
	LTTD = Column("LTTD", Float)
	DataSourceID = Column("DataSourceID", Integer)


class ForeRainData(model_base):
	__tablename__ = "ForeRainData_M_B"
	TID = Column("TID", Integer, primary_key=True, autoincrement=True)
	PID = Column("PID", Integer, nullable=False)
	TM = Column("TM", DateTime, nullable=False)
	DRP = Column("DRP", Float)


class Points:
	def __init__(self, lgtd, lttd):
		self.lgtd = lgtd
		self.lttd = lttd

	def __hash__(self):
		return hash(str(self.lgtd) + str(self.lttd))

	def __eq__(self, other):
		if self.lttd == other.lttd and self.lgtd == other.lgtd:
			return True
		return False


fore_point_dict = dict()


def add_hunan_point(model_str=None):
	point_list = list()
	for i in range(0, 13456):
		lgtd = (i % 116) * 0.05 + 108.65
		lttd = 30.25 - (i // 116) * 0.05
		tmp_record = ForeRainPoint(LGTD=lgtd, LTTD=lttd, DataSourceID=4301)
		point_list.append(tmp_record)
	if not model_str:
		model_str = 'mssql+pyodbc://sa:3edc9ijn~@192.168.0.151/TZX_RES_MODEL_SHYJ?driver=sql+server'
	engine = create_engine(model_str, echo=True)
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	session.add_all(point_list)
	session.commit()
	session.close()


def load_fore_point(model_conn_str):
	session = get_session(model_conn_str)
	rets = session.query(ForeRainPoint).filter(ForeRainPoint.DataSourceID == 21).all()
	for r in rets:
		p = Points(round(r.LGTD, 2), round(r.LTTD, 2))
		fore_point_dict[p] = r.PID
	session.close()


def task_thread(base_time: datetime, wfhour: int, data_str: str, model_conn_str):
	target_time = base_time + timedelta(hours=wfhour)
	assert len(data_str) > 2
	data_str.strip('')
	data_str = data_str[1:-1]  # 去除头尾的 {}
	ceils = data_str.split(',')
	assert len(ceils) == 116 * 116
	fore_data = list()
	for i in range(0, 116 * 116):
		lgtd = (i % 116) * 0.05 + 108.65
		lttd = 30.25 - (i // 116) * 0.05
		pid = fore_point_dict[Points(round(lgtd, 2), round(lttd, 2))]
		fore_data.append(ForeRainData(PID=pid, TM=target_time, DRP=float(ceils[i])))
	model_session = get_session(model_conn_str)
	model_session.add_all(fore_data)
	model_session.commit()
	fore_data.clear()
	model_session.close()


def proc_task(base_time, model_conn_str, fore_conn_str):
	wfdatetime = '{:0>4d}{:0>2d}{:0>2d}{:0>2d}00'.format(base_time.year, base_time.month, base_time.day, base_time.hour)
	model_session = get_session(model_conn_str)
	fore_session = get_session(fore_conn_str)
	print(wfdatetime)
	# if wfdatetime is not None: #or model_time < wfdatetime:  # 目标数据库中没有改时间的数据
	results = fore_session.query(GribWeatherFore).filter(and_(GribWeatherFore.wfdatetime == wfdatetime, GribWeatherFore.wfhour <=12)).all()
	if len(results) == 0:
		print("Time : {0} not exist".format(wfdatetime))
	thread_list = list()
	for r in results:
		t = Thread(target=task_thread, args=(base_time, r.wfhour, r.data, model_conn_str,))
		thread_list.append(t)
		t.start()
		# task_thread(base_time, r.wfhour, r.data, model_conn_str)

	is_finish = False
	while not is_finish:
		is_finish = True
		for t in thread_list:
			if t.isAlive():
				is_finish = False
				break
		sleep(2)
	fore_session.close()

	print(1)


if __name__ == '__main__':
	# add_hunan_point()
	parser = argparse.ArgumentParser(description='配置文件路径')
	parser.add_argument('path', type=str, help='配置文件路径')
	args = parser.parse_args()
	config = toml.load(args.path)
	model_str = config.get("fore").get("model")
	#'mssql+pyodbc://sa:3edc9ijn~@192.168.0.151/TZX_RES_MODEL_SHYJ?driver=sql+server'
	fore_str = config.get("fore").get("forerwdb")
	start_time_str = config.get("fore").get("start_time")
	#'mssql+pyodbc://sa:123456@.\\dly/hunanfore?driver=sql+server'
	load_fore_point(model_str)
	start_time = time_from_str(start_time_str)
	while model_str is not None and fore_str is not None:
		thread_list2 = list()
		# 202110110800
		temp_time = datetime(year=2021, month=10, day=11, hour=20)
		while start_time < temp_time:
			# t1 = Thread(target=proc_task, args = [start_time, model_str, fore_str])
			proc_task(start_time, model_str, fore_str)
			# thread_list2.append(t1)
			# t1.start()
			start_time = start_time + timedelta(hours=12)

		# is_all_done = False
		# while not is_all_done:
		# 	is_all_done = True
		# 	for t1 in thread_list2:
		# 		if t1.isAlive():
		# 			is_all_done =False
		# 			break
		# 	sleep(3)

	print('Exiting..')
	time.sleep(5)
	sys.exit(0)
