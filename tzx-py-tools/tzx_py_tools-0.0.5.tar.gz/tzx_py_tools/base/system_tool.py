#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   system_tool.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/21 12:26     douly      1.0         system_tool
"""
# import lib


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


def is_number(s):
	"""
	判断给定的字符串能否被转为浮点数

	:param s:
	:return:
	"""
	try:
		float(s)
		return True
	except ValueError:
		pass

	try:
		import unicodedata
		unicodedata.numeric(s)
		return True
	except (TypeError, ValueError):
		pass

	return False
