#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：kevinleong1011@hotmail.com
@desc: 
"""
import inspect
from datetime import datetime
from uuid import UUID

from . import const


def serialize(o, fields=None, exclude_fields=None, dt_fmt=const.DEFAULT_TIME_FORMAT):
    """
    序列化对象

    :param o:
    :param fields: 序列化字段，list类型，但内部项可以是字段名和序列化方法的键值对字典
    :param exclude_fields: 排除的字段
    :param dt_fmt: 日期时间格式化字符串，默认：'%Y-%m-%d %H:%M:%S'
    :return: 对于 str, int, float, bool 普通类型，返回原值；UUID直接str转换；若对象实现serialize，则执行该方法；否则根据字段要求提取
    """
    if isinstance(o, (str, int, float, bool)):
        return o
    elif isinstance(o, datetime):
        return o.strftime(dt_fmt)
    elif isinstance(o, UUID):
        return str(o)
    elif isinstance(o, list):
        return [serialize(item, fields=fields, exclude_fields=exclude_fields) for item in o]
    if hasattr(o, 'serialize') and inspect.isroutine(o.serialize):
        return o.serialize()
    d = dict()
    for name in dir(o):
        value = getattr(o, name)
        if callable(value):
            continue
        elif name.startswith('__') and name.endswith('__'):
            continue
        if exclude_fields:
            if name in exclude_fields:
                continue
        if fields:
            for f in fields:
                if isinstance(f, dict):
                    for f_name, f_serialize in f.items():
                        if f_name != name:
                            continue
                        fv = f_serialize(value)
                        d[f_name] = fv
                elif isinstance(f, str) and name == f:
                    d[f] = serialize(value, fields=fields, exclude_fields=exclude_fields)
            continue
        else:
            d[name] = serialize(value)
    return d
