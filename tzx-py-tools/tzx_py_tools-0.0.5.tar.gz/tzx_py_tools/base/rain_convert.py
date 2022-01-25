#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   rain_convert.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/7/8 17:27     douly      1.0         rain_convert
"""
# import lib

import math
from datetime import datetime, timedelta

stcds = {'31032050': '吕庄', '31032370': '保店', '31032410': '相衙', '31032420': '时集', '31105201': '李官屯', '31120350': '张鲁',
         '31120700': '贾镇', '31121140': '于集', '31121400': '三十里铺', '31121500': '夏津', '31121980': '义渡口', '31122000': '平原',
         '31122130': '丁庄', '31122140': '滋镇', '31122150': '神头', '31122210': '宋家', '31122220': '柴胡店', '31122300': '德平',
         '31122410': '丁坞', '31122420': '铁营', '31122740': '王庙', '31122750': '林庄', '31002001': '埕口', '31032400': '大赵',
         '31032440': '大柳', '31032470': '胡家', '31032480': '朱集', '31101487': '马才', '31120450': '王奉', '31121250': '旧城',
         '31121710': '王杲铺', '31121940': '边临镇', '31121960': '徽王庄', '31121970': '前孙', '31122450': '黄夹', '31122500': '乐陵',
         '31123030': '宿安', '31123050': '理合', '31123230': '东辛店', '31123250': '孙集', '31123500': '观城', '31124900': '乐平铺',
         '31125000': '杜郎口', '31125170': '安仁', '31000401': '德州', '31000401': '德州', '31032390': '赵虎', '31032430': '西葛勇',
         '31032460': '刘武官', '31032630': '严务', '31101701': '无棣', '31103601': '禹城', '31121350': '松林', '31121510': '夏津水库',
         '31121575': '苏留庄', '31121660': '王大卦', '31121670': '三唐', '31121700': '恩城', '31122100': '陵城区', '31122550': '庆云',
         '31122700': '苏集', '31122710': '相家河水库', '31122850': '郑家寨', '31122880': '梁家', '31122900': '张集',
         '31122990': '兴隆寺', '31031850': '老武城', '31032000': '李家户', '31032450': '长官', '31032490': '张大庄', '31032640': '崔口',
         '31101187': '腰站', '31102901': '莘县', '31120600': '冠县', '31120900': '柳林', '31121200': '薛王刘闸', '31121450': '香赵庄',
         '31121460': '东李官屯', '31121490': '宋楼', '31121550': '高唐', '31122230': '杜集', '31122250': '糜镇', '31122350': '宁津',
         '31122360': '宁津水库', '31122400': '化家', '31122800': '王凤楼', '31122810': '坊子', '31122890': '张庄', '31125180': '房寺',
         '31125200': '徐屯', '31125350': '东阿', '31125540': '潘店', '31125850': '焦庙', '31125860': '祝阿', '31126360': '表白寺',
         '31126500': '崔许闸', '31126800': '淄角镇', '31127450': '阳信', '31127550': '富国', '4142800B': '四里庄', '31122760': '前曹',
         '31123000': '临邑', '31123101': '孙庵', '31125500': '马集', '31125560': '赵官', '31126180': '莒镇', '31126190': '伦镇',
         '31126210': '大黄', '31126450': '夏口', '31126550': '孙耿', '31126600': '垛石', '31126850': '大年陈', '31126900': '申家桥',
         '31127300': '垛圈', '31127350': '温店', '31127700': '佘家', '31128100': '利国', '31128200': '义和庄', '4142804B': '兴隆村',
         '4142805B': '贾庄', '418C221A': '大桥', '31122950': '营子', '31122980': '临南', '31123010': '临盘', '31123040': '林子',
         '31123210': '尚堂', '31123750': '朝城', '31123950': '阳谷', '31124550': '沙镇', '31124600': '阎觉寺', '31125150': '辛寨',
         '31125160': '前油坊', '31125570': '胡官屯', '31125700': '刘桥', '31126350': '晏城', '31126650': '济阳', '31126750': '仁风',
         '31127050': '麻店', '31127088': '惠民', '31127950': '北镇', '31128350': '刁口', '41820200': '同兴', '418C214A': '靳家',
         '31123020': '翟家', '31123150': '商河', '31123190': '杨安镇', '31123225': '中丁', '31123450': '古云', '31124200': '安乐镇',
         '31124450': '于集2', '31124850': '固河', '31124950': '茌平', '31126200': '仁里集', '31126300': '齐河', '31126370': '安头',
         '31126700': '白桥', '31127100': '里则镇', '31128000': '单寺', '31128150': '新户', '31128250': '汀河'}


class RainData(object):
	def __init__(self, s, t, i=1, d=0):
		assert isinstance(t, datetime)
		self.stcd = s
		self.time = t.replace(second=0)  # set second to 0, avoid some question where split rain fall to each hour.
		self.intv = i  # default unit is hour, if i < 0, then i * 100 (minutes), i must be less than 0.6
		self.drp = d

	def spilt(self):
		"""
		将降雨数据逐小时分割

		Args:
			self (RainData): Rain data object

		Returns:
			dict : 整点时间和降雨量的键值对.

		"""
		h_list = dict()
		assert isinstance(self.time, datetime)
		assert self.intv > 0
		mins, hours = math.modf(self.intv)
		mins = mins * 100
		begin_time = self.time - timedelta(hours=hours, minutes=mins)
		total_seconds = timedelta(hours=hours, minutes=mins).total_seconds() / 60
		# intv and self.time cross day; intv and self.time across the same hour.
		t1 = begin_time - timedelta(minutes=begin_time.minute)
		t2 = begin_time + timedelta(minutes=(60 - begin_time.minute))
		if mins + self.time.second < 60:
			h_list[t2] = self.drp
			return h_list

		t3 = self.time - timedelta(minutes=self.time.minute)
		t4 = self.time + timedelta(minutes=(60 - begin_time.minute))

		while t2 < t3:
			t2 = t2 + timedelta(hours=1)
			h_list[t2] = self.drp * 60 * 60 / total_seconds

		if t4 not in h_list:
			h_list[t4] = self.drp * self.time.minute * 60 / total_seconds

		return h_list


class RainConvert(object):

	def __init__(self):
		pass

	@staticmethod
	def convert_to_hour(rds: list):
		"""
		将非整点的降雨数据,根据提供的INTV,转换未整点数据

		:param rds:
		:return:
		"""
		format_data = dict()
		for rd in rds:
			assert isinstance(rd, RainData)
			split_data = rd.spilt()
			if rd.stcd not in format_data:
				format_data[rd.stcd] = dict()
			for k, v in split_data:
				if k not in format_data[rd.stcd]:
					format_data[rd.stcd][k] = 0  # need add, if not exist, must initialize to 0.
				format_data[rd.stcd][k] += v

		return format_data