"""
pyape.util.func
~~~~~~~~~~~~~~~~~~~

工具类，依赖 config
放置和请求完全无关的，不依赖任何 flask 框架内容的工具
这个类应该可以被其它模块导入而不发生冲突
"""

from datetime import datetime, timedelta, date, time as time2
import re
import json


_simple_class = [int, float, str, bool, dict, list, datetime]


def issimple(value):
    """ 判断一个值是否为简单类型，包括 None
    """
    for typeclass in _simple_class:
        if value is None or isinstance(value, typeclass):
            return True
    return False


def parse_bool(value, default_value=False):
    if value is not None:
        return value.lower() == 'true'
    return default_value


def parse_int(value, default_value=None):
    if value is not None:
        try:
            value = int(value)
            return value
        except:
            return default_value
    return default_value


def parse_float(value, default_value=None):
    if value is not None:
        try:
            value = float(value)
            return value
        except:
            return default_value
    return default_value


def parse_date(value, default_value=None, to_day_end=False):
    """ 解析一个日期字符串
    :param value:
    :param default_value:
    :param to_day_end:  值为True 则自动加上23小时59分59秒999999微秒（当天的最后时刻），用来判断包含关系
    :return:
    """
    if value is None:
        value = default_value
    else:
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except:
            value = default_value
    if isinstance(value, datetime) and to_day_end:
        # 86399 = 3600*24-1
        value += timedelta(seconds=86399, microseconds=999999)
    return value


def between_date(from_date, to_date):
    """ 传递一个 from_date 和 一个 to_date，返回中间所有的 date（包括 from_date 和 to_date）
    """
    fd = date(from_date.year, from_date.month, from_date.day)
    td = date(to_date.year, to_date.month, to_date.day)
    days = [fd]
    # from 和 to 是同一天
    if fd == td:
        return days
    # from 在 to 之后，以 from 为准
    if fd > td:
        return days
    ld = date(fd.year, fd.month, fd.day)
    while ld < td:
        ld += timedelta(days=1)
        days.append(ld)
    return days


def strfdate(dtobj):
    """ 将一个 datetime 转换成成 YYYY-MM-DD 形式的字符串
    :param dtobj: datetime 实例
    :return:
    """
    return dtobj.strftime('%Y-%m-%d')


def strptime(timestr):
    """ 将一个 time 字符串按照 HH:MM:SS 形式的字符串转换成 datetime.time 对象
    :param timestr: 时间字符串
    :return: datetime.time
    """
    dt = datetime.strptime(timestr, '%H:%M:%S')
    return time2(dt.hour, dt.minute, dt.second)


def in_time_range(timestart, timeend, dt=None):
    """ 判断给定的时间 dt 是否在两个时间中间。
    :param timestart: 开始的时间，支持字符串和 time 对象，字符串使用本模块中的 strptime 解析
    :param timeend: 结束的时间，支持字符串和 time 对象，字符串使用本模块中的 strptime 解析
    :param dt: 给定的 datetime 对象，如果不提供则使用 datetime.now()
    :return: boolean
    """
    if isinstance(timestart, str):
        timestart = strptime(timestart)
    if isinstance(timeend, str):
        timeend = strptime(timeend)
    if dt is None:
        dt = datetime.now()
    dtstart = datetime(dt.year, dt.month, dt.day, timestart.hour, timestart.minute, timestart.second)
    dtend = datetime(dt.year, dt.month, dt.day, timeend.hour, timeend.minute, timeend.second)
    # 如果 timeend 小于 timestart，就将 timeend 增加一天。
    if timeend < timestart:
        dtend += timedelta(days=1)
    return dt > dtstart and dt < dtend


def next_month_dt(day=None):
    """ 返回下一个月的 datetime 对象
    :param day: 基准 datetime 对象
    :return:
    """
    if day is None:
        day = date.today()
    m = day.month + 1
    y = day.year
    if m > 12:
        # 处理跨年
        m = 1
        y += 1
    return datetime(y, m, 1)


def last_month_dt(day=None):
    """ 返回上个月的 datetime 对象
    :param day: 基准 datetime 对象
    :return:
    """
    if day is None:
        day = date.today()
    # 找到上个月
    m = day.month - 1
    y = day.year
    if m <= 0:
        # 处理跨年
        m = 12
        y -= 1
    return datetime(y, m, 1)


def daydt(day=None, default_initday=False, first_day_of_month=False):
    """ 获取一个hour为0的日期
    :param day: 时间戳或者基准 date/datetime 对象
    :param default_initday: 仅当 day 参数为 None 的时候有效，True 代表使用初始日期，否则使用今天
    :param first_day_of_month: 值为 True 则返回提供的 day 所在月的第一天
    :return:
    """
    if not day:
        if default_initday:
            day = date(2017, 10, 15)
        else:
            day = date.today()
    elif isinstance(day, int):
        day = datetime.fromtimestamp(day)
    return datetime(day.year, day.month, 1 if first_day_of_month else day.day)


def get_cur_and_next_month(day=None):
    """ 获取代表本月到下月的日期对象
    :param day: 一个 datetime 对象，基于这个对象作为基准来创建 cur_month
    :return:
    """
    # 如果不传递则使用今天作为基准
    if day is None:
        day = date.today()
    # 今天所在的月的第一天
    cur_month = datetime(day.year, day.month, 1)
    return cur_month, next_month_dt(cur_month)


def _json_datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


def jsondumps(obj):
    """ dump 一个 json 字符串，处理 datetime
    :param obj:
    :return:
    """
    return json.dumps(obj, default=_json_datetime_handler)

PVER_RE = re.compile(r'([abr])\d+', re.I)

def vername2code(vername):
    """ 转换 vername 到 vercode
    每个版本位允许3位
    :param vername:
    :return:
    """
    try:
        verlist = vername.split('.')
        vercode = 0
        if len(verlist) > 2:
            vercode += int(verlist[2])
        if len(verlist) > 1:
            vercode += int(verlist[1]) * 1000
        vercode += int(verlist[0]) * 1000000
        return vercode
    except Exception as e:
        return -1

