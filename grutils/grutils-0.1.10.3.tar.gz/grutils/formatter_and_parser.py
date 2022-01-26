#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, date
from typing import List


def is_none_or_empty(s: any):
    return (type(s) == str and len(s) == 0) or (s is None)


def strip_if_str(s):
    if type(s) == str:
        return s.strip()
    else:
        return s


def parse_as_str_if_float_or_int(v):
    if type(v) == float:
        i = int(round(v, 0))
        return '{}'.format(i)
    elif type(v) == int:
        return '{}'.format(v)
    else:
        return v


def date_of(a: any):
    t = type(a)
    if t == str:
        if a.find('/') >= 0:
            items: List[str] = a.split('/')
            items_count = len(items)
            if items_count == 2:
                month = int(items[0])
                day = int(items[1])
                today = datetime.date(datetime.now())
                month_diff = today.month - month
                year = today.year if (0 <= month_diff <= 8) else (today.year + 1)
                return date.fromisoformat('{:04d}-{:02d}-{:02d}'.format(year, month, day))
            elif items_count == 3:
                month = int(items[0])
                day = int(items[1])
                year = int(items[2])
                return date.fromisoformat('{:04d}-{:02d}-{:02d}'.format(year, month, day))
        elif a.find('-') >= 0:
            items: List[str] = a.split('-')
            if len(items) == 3:
                year = int(items[0])
                month = int(items[1])
                day = int(items[2])
                return date.fromisoformat('{:04d}-{:02d}-{:02d}'.format(year, month, day))
        raise Exception('not found splitter / or - in raw string')
    elif t == datetime:
        return a.date()
    elif t == date:
        return a
    else:
        raise Exception('invalid raw data type: {}'.format(t))


def float_02(f: float):
    return round(f * 100) / 100


def str_without_prefix(val: any, prefix='\''):
    if type(val) == str and val.startswith(prefix):
        return val[len(prefix):]
    else:
        return val


def str_without_prefixes(val: any, prefixes: List[str]):
    if type(val) != str:
        return val
    _val = val
    for prefix in prefixes:
        if _val.startswith(prefix):
            _val = _val[len(prefix):]
    return _val


def str_with_prefix(val: any, formatter: str = '{}', prefix='\''):
    if type(val) == str and val.startswith(prefix):
        return val
    else:
        return (prefix + formatter).format(val)


def simple_date_str(d: date):
    return '{}/{}'.format(d.month, d.day)


def string_of(v: any):
    return v if type(v) == str else '{}'.format(v)


def bool_of(v: any):
    if type(v) == str:
        _v = "".lower().strip()
        return _v in ["是", "true", "t"]
    elif type(v) == bool:
        return v
    else:
        raise Exception('invalid type {}'.format(type(v)))


# noinspection PyBroadException
def parse_value(val, data_type: str = "自动", raise_exception=True):
    if data_type == "自动":
        return val

    if isinstance(val, list):
        return list(map(lambda x: parse_value(x, data_type, raise_exception), val))

    _val = strip_if_str(val)
    try:
        if data_type == "文本":
            _val = parse_as_str_if_float_or_int(val)
            if type(_val) != str:
                _val = '{}'.format(_val)
            return _val

        if type(_val) == str:
            _val = str_without_prefixes(_val, ["'", "`"])
        if data_type == "整数":
            return int(round(float(_val)))

        if data_type == "小数":
            return float(_val)

        if data_type == "日期":
            return date_of(_val)

        if data_type == "是否":
            return bool_of(_val)
    except Exception as e:
        if not raise_exception:
            return None

        msg = 'failed with parse {} from ({}), details: {}'.format(data_type, val, e)
        return Exception(msg)

    msg = 'unsupported data type ({})'.format(data_type)
    return Exception(msg)
