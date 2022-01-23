# encoding=utf-8
# @Time    : 2022/1/23 15:39
# @Author  : YangBiao
# @Email   : 19921297590@126.com
# @File    : custom_time.py
# @Version : 1.0
# @Python  : python 3.7.2


import datetime
import re
from types import BuiltinFunctionType, BuiltinMethodType

__DEFAULT_TIME_FORMAT__ = '%Y-%m-%d %H:%M:%S'


class CustomTime:

    def __init__(self, time_str, except_format=None, ):
        # 输入的原始字符串
        self.orig_str = time_str
        # 识别字符串格式
        self.orig_str_format = self._spot_date_(self.orig_str)

        # 使用这个字符串初始化datetime对象
        try:
            self._obj = datetime.datetime.strptime(self.orig_str, self.orig_str_format)
        except Exception as err:
            # log.error(err, orig_str=self.orig_str, orig_str_format=self.orig_str_format)
            raise ValueError('初始化时间对象失败, 字符串与格式不匹配,或时间范围超限.')

        # 使用期望的格式格式化字符串
        self._str = self._obj.strftime(except_format) if except_format is not None else self.orig_str
        # 当前字符串的格式
        self.str_format = except_format if except_format is not None else self.orig_str_format

    @classmethod
    def _spot_date_(cls, time_str):
        # 使用正则表达式识别字符串格式
        # eg ; 输入2021-08-04 00:00:00.120
        # result = {'year': '2021', 's1': '-',
        #           'month': '08', 's2': '-',
        #           'day': '04', 's3': ' ',
        #           'hour': '00', 's4': ':',
        #           'minute': '00', 's5': ':',
        #           'second': '00', 's6': '.',
        #           'microsecond': '120'}
        pattern = r'''^(?P<year>\d{4})(?P<s1>(\W|)+)''' \
                  r'''(?P<month>(\d{2}|))(?P<s2>(\W|)+)''' \
                  r'''(?P<day>(\d{2}|))(?P<s3>(\W|)+)''' \
                  r'''(?P<hour>(\d{2}|))(?P<s4>(\W|)+)''' \
                  r'''(?P<minute>(\d{2}|))(?P<s5>(\W|)+)''' \
                  r'''(?P<second>(\d{2}|))(?P<s6>(\W|)+)''' \
                  r'''(?P<microsecond>(\d{3}|))$'''
        c = re.compile(pattern)
        d = c.match(time_str)
        result = d.groupdict()

        format_dict = {
            'year': '%Y', 'month': '%m', 'day': '%d',
            'hour': '%H', 'minute': '%M', 'second': '%S', 'microsecond': '%f'
        }

        for k, v in format_dict.items():
            v_ = result.get(k, None)
            if v_ in (None, ''):
                format_dict[k] = ''

        _dict = {k: v for k, v in result.items() if k not in format_dict}

        format_dict.update(_dict)
        format_str = '{year}{s1}{month}{s2}{day}{s3}{hour}{s4}{minute}{s5}{second}{s6}{microsecond}'.format_map(format_dict)
        return format_str

    def __getattr__(self, item):
        # 通过这个方法,调用datetime本身的属性和方法
        # 获取到该属性或者方法a
        a = getattr(self._obj, item, None)
        # 如果没有获取到,或者本身就是None,返回None
        if a is None:
            return None
        # 如果是方法, 定义一个inner方法,将调用的参数传入,执行后返回结果
        # 如果结果是datetime类,使用该结果,初始化一个当前类对象
        elif isinstance(a, BuiltinFunctionType) or isinstance(a, BuiltinMethodType):
            def inner(*args, **kwargs):
                r = a(*args, **kwargs)
                if isinstance(r, datetime.datetime):
                    return CustomTime(r.strftime(self.str_format), self.str_format)
                return r

            return inner
        # 如果是属性,返回该属性
        else:
            return a

    def __str__(self):
        return self._str

    def __add__(self, other):
        # 加法运算时,使用obj进行计算
        if isinstance(other, CustomTime):
            other = other.obj
        r = self._obj.__add__(other)

        if isinstance(r, datetime.datetime):
            return self._from_datetime(r, self.str_format)
        return r

    def __sub__(self, other):
        # 减法计算时,使用obj进行计算
        if isinstance(other, CustomTime):
            other = other.obj
        r = self._obj.__sub__(other)

        if isinstance(r, datetime.datetime):
            return self._from_datetime(r, self.str_format)
        return r

    def __lt__(self, other):
        return self._obj.__lt__(other.obj)

    def __gt__(self, other):
        return self._obj.__gt__(other.obj)

    def __le__(self, other):
        return self._obj.__le__(other.obj)

    def __ge__(self, other):
        return self._obj.__ge__(other.obj)

    def __eq__(self, other):
        return self._obj.__eq__(other.obj)

    @property
    def str(self):
        return self._str

    @property
    def obj(self):
        return self._obj

    def date(self, format=None):
        format = self.str_format.split('%d')[0] + '%d' if format is None else format
        return self._obj.strftime(format)

    @classmethod
    def now(cls, except_format=__DEFAULT_TIME_FORMAT__):
        # 因为__getattr__()方法只对实例化对象起作用,使用类调用时报错,所以想使用datetime的类方法需要重写
        now = datetime.datetime.now()
        return cls._from_datetime(now, except_format)

    @property
    def timestamp(self):
        return int(self._obj.timestamp())

    def delta(self, years=0, months=0, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        delta_ = datetime.timedelta(days=days,
                                    seconds=seconds,
                                    microseconds=microseconds,
                                    milliseconds=milliseconds,
                                    minutes=minutes,
                                    hours=hours,
                                    weeks=weeks)
        time_middle_1 = self._obj + delta_

        # 一共差多少个月，下面称为z总偏移量，可正可负
        months_ = months + years * 12
        month_rel = months_ + time_middle_1.month
        # log.debug(month_rel=month_rel)
        years_delta, month = divmod(month_rel, 12)
        # log.debug(years_delta=years_delta, months_delta=month)
        years_delta, month = (years_delta - 1, 12) if month == 0 else (years_delta, month)
        year = years_delta + time_middle_1.year
        time_obj = time_middle_1.replace(year=year, month=month)
        return self._from_datetime(time_obj, self.str_format)

    @classmethod
    def _from_datetime(cls, time_obj, except_format=__DEFAULT_TIME_FORMAT__):
        return cls(time_obj.strftime(except_format), except_format)

    def oclock(self):
        obj = self.obj.replace(second=0, microsecond=0, minute=0)
        return self._from_datetime(obj, self.str_format)
