#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   web_tool.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/15 11:16     douly      1.0         web_tool
"""
# import lib
from flask import Response


def response_headers(content: str):
	"""


	:param content:
	:return:
	"""
	resp = Response(content)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp


def response_headers_json(content: str):
	"""
	返回json的response, 完成跨域

	:param content: json str
	:return:
	"""
	resp = Response(content)
	resp.content_type = 'application/json'
	resp.headers['Access-Control-Allow-Method'] = '*'
	resp.headers['Access-Control-Allow-Headers'] = '*'
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp


def response_headers_png(content):
	resp = Response(content)
	resp.content_type = 'image/png'
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp
