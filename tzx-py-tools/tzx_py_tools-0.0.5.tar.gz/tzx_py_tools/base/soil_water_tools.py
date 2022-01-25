#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   soil_water_tools.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021-12-16 13:29     douly      1.0         soil_water_tools
"""


# import lib


def calc_soil_data(pptn_data: dict, wms, kas, last_soil, reduce=0.6):
	"""
	计算含水量数据

	:param pptn_data: 降雨数据 {point:{TM, DRP}} ,TM需要整理为整点数据
	:param wms: 持水量
	:param kas: 折减系数
	:param last_soil:上个时刻的含水率
	:param reduce: 没有上个时刻含水率时的初值折减
	:return:
	"""
	data_begin_tm = max(pptn_data.keys())

	for _p, _wm in wms.items():
		_ka = kas[_p]
		_last_val = 0.6 * _wm
		if _p in last_soil:
			_last_val = last_soil[_p]
	#
	for _p, records in pptn_data.items():
		_tmp_record = last_soil.copy()  # 含水百分比 %
		_wm = wms[_p]
		for _tm, _drp in records.items():
			_last_soil = reduce * _wm
			if _p in _tmp_record:
				_last_soil = _tmp_record[_p] / 100.0 * _wm

			_this_soil_w = min(kas[_p] * (_last_soil + _drp), _wm)
			swp = _this_soil_w / _wm
			_tmp_record[_p] = int(swp * 100)  # 含水率
