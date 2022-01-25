#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   clock_tool.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/5 9:37     douly      1.0         clock_tool
"""
# import lib
import json
import re
from datetime import datetime, timedelta

import redis


def to_standard_hour(tm: datetime, hs: list):
	"""
	传入的时间转为标准数据时间

	:param tm: 时间
	:param hs: 标准hour , 由大到小排列
	:return:
	"""
	assert len(hs)
	hs.sort(reverse=True)
	h = tm.hour
	for th in hs:
		if h > th:
			return datetime(year=tm.year, month=tm.month, day=tm.day, hour=th)

	return datetime(year=tm.year, month=tm.month, day=tm.day, hour=hs[0]) - timedelta(days=1)


REFMT1 = r"(\d{4}-\d{1,2}-\d{1,2})"
REFMT2 = r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2})"
REFMT3 = r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})"
REFMT4 = r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})"

DFT1 = '%Y-%m-%d'
DFT2 = '%Y-%m-%d %H'
DFT3 = '%Y-%m-%d %H:%M'
DFT4 = '%Y-%m-%d %H:%M:%S'
DFT6 = '%Y%m%d%H%M'
DFT7 = '%m/%d %H'
DFT21 = '%Y%m%d%H'
DFT22 = '%Y年%m月%d日%H时'

DFT51 = '%H时%M分'


def time_from_str(time_str: str):
	"""
	从字符串转化为datetime对象

	:param time_str:
	:return:
	"""
	try:
		mat = re.findall(REFMT4, time_str)
		if len(mat) > 0:
			return datetime.strptime(time_str, DFT4)
		mat = re.findall(REFMT3, time_str)
		if len(mat) > 0:
			return datetime.strptime(time_str, DFT3)
		mat = re.findall(REFMT2, time_str)
		if len(mat) > 0:
			return datetime.strptime(time_str, DFT2)
		mat = re.findall(REFMT1, time_str)
		if len(mat) > 0:
			return datetime.strptime(time_str, DFT1)
	except Exception as e:
		print(e)

	return None


def update_time_from_redis(redis_client: redis.Redis, topic: str, method):
	"""
	更新时间监视

	:param redis_client: redis 客户端
	:param topic: 订阅主题
	:param method: 执行方法
	:return:
	"""
	# rc = redis.StrictRedis(host=addr, port=port, password=redis_pwd)
	while True:
		ps = redis_client.pubsub()
		ps.subscribe(topic)
		for item in ps.listen():  # 监听状态：有消息发布了就拿过来
			if item['type'] == 'message':
				time = json.loads(str(item['data'], encoding='utf-8'))['end_time']
				print(time)
				ftime = time_from_str(time)
				try:
					method(ftime)
				except Exception as e:
					print(e)

