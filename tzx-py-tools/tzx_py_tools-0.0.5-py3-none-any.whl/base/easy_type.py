#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   easy_type.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021-12-10 18:17     douly      1.0         easy_type
"""
# import lib
from pydantic import BaseModel


class GeoRect(BaseModel):
	left: float
	right: float
	top: float
	bottom: float


class GeoPoint(BaseModel):
	lgtd: float
	lttd: float


class ScreenRect(BaseModel):
	width: int
	height: int


class ScreenPoint(BaseModel):
	x: int
	y: int

