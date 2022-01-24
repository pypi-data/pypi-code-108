'''
:Author: ChenXiaolei
:Date: 2020-03-06 23:17:54
:LastEditTime: 2020-03-21 16:50:31
:LastEditors: ChenXiaolei
:Description: time helper
'''
# -*- coding: utf-8 -*-

import time
import datetime
from dateutil.relativedelta import relativedelta


class TimeHelper:
    @classmethod
    def format_time_to_datetime(self,
                                format_time=None,
                                format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 时间字符串转datetime
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        if not format_time:
            return datetime.datetime.now()
        return datetime.datetime.strptime(format_time, format)

    @classmethod
    def format_time_convert_format(self,
                                   format_time=None,
                                   format_before='%Y-%m-%d %H:%M:%S',
                                   format_after='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 转换格式时间的格式
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param format_before: 格式化之前的时间格式
        :param format_after: 希望转换格式化后的时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        if not format_time:
            return self.get_now_format_time(format=format_after)
        return self.datetime_to_format_time(self.format_time_to_datetime(
            format_time, format_before),
                                            format=format_after)

    @classmethod
    def datetime_to_format_time(self, dt, format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: datetime转时间字符串
        :param dt: datetime格式时间
        :param format: 格式化时间格式
        :return: 时间字符串
        :last_editors: ChenXiaolei
        """
        return dt.strftime(format)

    @classmethod
    def datetime_to_timestamp(self,
                              dt,
                              format='%Y-%m-%d %H:%M:%S',
                              out_ms=False):
        """
        :Description: datetime转unix时间戳
        :param dt: datetime格式时间
        :param format: 格式化时间格式
        :return: unix时间戳
        :last_editors: ChenXiaolei
        """
        if out_ms:
            return int(
                time.mktime(dt.timetuple()) * 1000.0 + dt.microsecond / 1000.0)
        return int(time.mktime(dt.timetuple()))

    @classmethod
    def format_time_to_timestamp(self,
                                 format_time=None,
                                 format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 格式化时间转为Unix时间戳
        :param format_time: 格式化时间，如果未传则返回服务器当前时间
        :param format: 格式化时间格式
        :return: Unix时间戳
        :last_editors: ChenXiaolei
        """
        if format_time:
            time_tuple = time.strptime(format_time, format)
            result = time.mktime(time_tuple)
            return int(result)
        return int(time.time())

    @classmethod
    def timestamp_to_format_time(self,
                                 timestamp=None,
                                 format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 时间戳转格式化时间
        :param timestamp: unix时间戳
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        if timestamp:
            time_tuple = time.localtime(timestamp)
            result = time.strftime(format, time_tuple)
            return result
        else:
            return time.strftime(format)

    @classmethod
    def timestamp_to_datetime(self, timestamp=time.time()):
        """
        :Description: unix时间戳转datetime
        :param timestamp: unix时间戳，如果没传默认取服务器当前时间
        :return: datetime
        :last_editors: ChenXiaolei
        """
        if self.is_ms_timestamp(timestamp):
            timestamp = timestamp / 1000
        return datetime.datetime.fromtimestamp(timestamp)

    def change_format_time(self,
                           in_format_time=None,
                           in_format='%Y-%m-%d %H:%M:%S',
                           out_format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 更改格式化时间格式
        :param in_format_time: 更改前格式化时间字符串
        :param in_format: 更改前格式化时间格式
        :param out_format: 需更改的格式化时间格式
        :return: 格式化时间字符串
        :last_editors: ChenXiaolei
        """
        return self.timestamp_to_format_time(
            self.format_time_to_timestamp(in_format_time, in_format),
            out_format)

    @classmethod
    def get_now_timestamp(self, is_ms=False):
        """
        :Description: 获取当前时间戳
        :param is_ms: 是否输出毫秒级时间戳 是-True 否-False
        :return: 时间戳
        :last_editors: ChenXiaolei
        """
        if is_ms:
            return int(round(time.time() * 1000))
        else:
            return int(time.time())

    @classmethod
    def get_now_datetime(self):
        """
        :Description: 获取当前时间格式
        :return: 格式化时间
        :last_editors: ChenXiaolei
        """
        return datetime.datetime.now()

    @classmethod
    def get_now_format_time(self, format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 获取当前时间格式
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        return datetime.datetime.now().strftime(format)

    @classmethod
    def is_ms_timestamp(self, timestamp):
        """
        :Description: 时间戳是否为毫秒时间戳
        :param timestamp: unix时间戳
        :return: bool
        :last_editors: ChenXiaolei
        """
        if timestamp and len(str(int(timestamp))) > 10:
            return True
        else:
            return False

    @classmethod
    def add_seconds_by_timestamp(self, timestamp=None, second=1):
        """
        :Description: 为时间戳增加秒数
        :param timestamp: unix时间戳
        :param second: 秒数
        :return: unix时间戳
        :last_editors: ChenXiaolei
        """
        if not timestamp:
            timestamp = self.get_now_timestamp()

        # 毫秒时间戳
        if self.is_ms_timestamp(timestamp):
            return timestamp + (second * 1000)
        else:
            return timestamp + second

    @classmethod
    def add_minutes_by_timestamp(self, timestamp=None, minute=1):
        """
        :Description: 为时间戳增加分钟数
        :param timestamp: unix时间戳
        :param minute: 分钟数
        :return: unix时间戳
        :last_editors: ChenXiaolei
        """
        return self.add_seconds_by_timestamp(timestamp, minute * 60)

    @classmethod
    def add_hours_by_timestamp(self, timestamp=None, hour=1):
        """
        :Description: 为时间戳增加小时数
        :param timestamp: unix时间戳
        :param hour: 小时数
        :return: unix时间戳
        :last_editors: ChenXiaolei
        """
        return self.add_seconds_by_timestamp(timestamp, hour * 3600)

    @classmethod
    def add_days_by_timestamp(self, timestamp=None, day=1):
        """
        :Description: 为时间戳增加天数
        :param timestamp: unix时间戳
        :param day: 天数
        :return: unix时间戳
        :last_editors: ChenXiaolei
        """
        return self.add_seconds_by_timestamp(timestamp, day * 86400)

    @classmethod
    def add_months_by_timestamp(self, timestamp=None, months=1):
        """
        :Description: 为时间戳增加月数
        :param timestamp: unix时间戳
        :param months: 月数
        :return: unix时间戳
        :last_editors: ChenXiaolei
        """
        if not timestamp:
            timestamp = time.time()

        dt = self.timestamp_to_datetime(timestamp)
        return self.datetime_to_timestamp(
            dt + relativedelta(months=months),
            out_ms=self.is_ms_timestamp(timestamp))

    @classmethod
    def add_years_by_timestamp(self, timestamp=None, years=1):
        """
        :Description: 为时间戳增加年数
        :param timestamp: unix时间戳
        :param years: 年数
        :return: unix时间戳
        :last_editors: ChenXiaolei
        """
        if not timestamp:
            timestamp = time.time()

        dt = self.timestamp_to_datetime(timestamp)
        return self.datetime_to_timestamp(
            dt + relativedelta(years=years),
            out_ms=self.is_ms_timestamp(timestamp))

    @classmethod
    def add_second_by_format_time(self,
                                  format_time=None,
                                  second=1,
                                  format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 为时间格式增加秒数
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param second: 秒数
        :return: datetime
        :last_editors: ChenXiaolei
        """
        return (self.format_time_to_datetime(format_time, format) +
                datetime.timedelta(seconds=second)).strftime(format)

    @classmethod
    def add_minutes_by_format_time(self,
                                   format_time=None,
                                   minute=1,
                                   format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 为时间格式增加分钟数
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param minute: 分钟数
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        return (self.format_time_to_datetime(format_time, format) +
                datetime.timedelta(minutes=minute)).strftime(format)

    @classmethod
    def add_hours_by_format_time(self,
                                 format_time=None,
                                 hour=1,
                                 format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 为时间格式增加小时数
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param hour: 小时数
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        return (self.format_time_to_datetime(format_time, format) +
                datetime.timedelta(hours=hour)).strftime(format)

    @classmethod
    def add_days_by_format_time(self,
                                format_time=None,
                                day=1,
                                format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 为时间格式增加天数
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param day: 天数
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        return (self.format_time_to_datetime(format_time, format) +
                datetime.timedelta(days=day)).strftime(format)

    @classmethod
    def add_months_by_format_time(self,
                                  format_time=None,
                                  months=1,
                                  format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 为时间格式增加月数
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param months: 月数
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        return (self.format_time_to_datetime(format_time, format) +
                relativedelta(months=months)).strftime(format)

    @classmethod
    def add_years_by_format_time(self,
                                 format_time=None,
                                 years=1,
                                 format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 为时间格式增加年数
        :param format_time: 格式化时间，如果未传则取服务器当前时间
        :param years: 年数
        :param format: 格式化时间格式
        :return: datetime
        :last_editors: ChenXiaolei
        """
        return (self.format_time_to_datetime(format_time, format) +
                relativedelta(years=years)).strftime(format)

    @classmethod
    def difference_datetime(self,
                            minuend_time,
                            subtracter_time,
                            format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 计算两个时间的差值,支持datetime/timstamp/format_time
        :param minuend_time: 被减时间
        :param subtracter_time: 减时间
        :return 时间差值(datetime)
        :last_editors: ChenXiaolei
        """
        if type(minuend_time) == datetime.datetime:
            minuend = minuend_time
        elif type(minuend_time) == int:
            minuend = self.timestamp_to_datetime(minuend_time)
        elif type(minuend_time) == str:
            minuend = self.format_time_to_datetime(minuend_time, format)
        else:
            raise Exception("minuend_time type error")

        if type(subtracter_time) == datetime.datetime:
            subtracter = subtracter_time
        elif type(subtracter_time) == int:
            subtracter = self.timestamp_to_datetime(subtracter_time)
        elif type(subtracter_time) == str:
            subtracter = self.format_time_to_datetime(subtracter_time, format)
        else:
            raise Exception("minuend_time type error")

        return minuend - subtracter

    @classmethod
    def difference_days(self,
                        minuend_time,
                        subtracter_time,
                        format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 计算两个时间的差值天数,支持datetime/timstamp/format_time
        :param minuend_time: 被减时间
        :param subtracter_time: 减时间
        :return 天数(int)
        :last_editors: ChenXiaolei
        """
        return self.difference_datetime(minuend_time,
                                        subtracter_time,
                                        format='%Y-%m-%d %H:%M:%S').days

    @classmethod
    def difference_seconds(self,
                           minuend_time,
                           subtracter_time,
                           format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 计算两个时间的差值秒数,支持datetime/timstamp/format_time
        :param minuend_time: 被减时间
        :param subtracter_time: 减时间
        :return 秒数(int)
        :last_editors: ChenXiaolei
        """
        return int(
            self.difference_datetime(
                minuend_time, subtracter_time,
                format='%Y-%m-%d %H:%M:%S').total_seconds())

    @classmethod
    def difference_minutes(self,
                           minuend_time,
                           subtracter_time,
                           format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 计算两个时间的差值分钟数,支持datetime/timstamp/format_time
        :param minuend_time: 被减时间
        :param subtracter_time: 减时间
        :return 分钟数(int)
        :last_editors: ChenXiaolei
        """
        return int(
            self.difference_seconds(
                minuend_time, subtracter_time, format='%Y-%m-%d %H:%M:%S') /
            60)

    @classmethod
    def difference_hours(self,
                         minuend_time,
                         subtracter_time,
                         format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 计算两个时间的差值小时数,支持datetime/timstamp/format_time
        :param minuend_time: 被减时间
        :param subtracter_time: 减时间
        :return 小时数(int)
        :last_editors: ChenXiaolei
        """
        return int(
            self.difference_seconds(
                minuend_time, subtracter_time, format='%Y-%m-%d %H:%M:%S') /
            60 / 60)

    @classmethod
    def get_first_day_of_the_week(self):
        """
        :Description: 获取本周一的日期
        :param 无
        :return datetime.date
        :last_editors: ChenXiaolei
        """
        now_datetime = self.get_now_datetime()
        return (now_datetime -
                datetime.timedelta(days=now_datetime.weekday())).date()

    @classmethod
    def get_last_day_of_the_week(self):
        """
        :Description: 获取本周日的日期
        :param 无
        :return datetime.date
        :last_editors: ChenXiaolei
        """
        now_datetime = self.get_now_datetime()
        return (now_datetime +
                datetime.timedelta(days=6 - now_datetime.weekday())).date()

    @classmethod
    def is_this_week(self, date, format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 指定时间是否在本周内
        :param date: 时间类型,支持timestamp/datetime/format_time
        :return 指定时间在本周内=True 指定时间不在本周内=False
        :last_editors: ChenXiaolei
        """
        compare_datetime = date
        if type(date) == int:
            compare_datetime = self.timestamp_to_datetime(date)
        elif type(date) == str:
            compare_datetime = self.format_time_to_datetime(date, format)
        if compare_datetime.date() >= self.get_first_day_of_the_week(
        ) and compare_datetime.date() <= self.get_last_day_of_the_week():
            return True
        return False

    @classmethod
    def get_first_day_of_the_month(self):
        """
        :Description: 获取本月第一天的日期
        :param 无
        :return datetime.date
        :last_editors: ChenXiaolei
        """
        now_datetime = self.get_now_datetime()
        return datetime.datetime(now_datetime.year, now_datetime.month, 1)

    @classmethod
    def get_last_day_of_the_month(self):
        """
        :Description: 获取本月最后一天的日期
        :param 无
        :return datetime.date
        :last_editors: ChenXiaolei
        """
        now_datetime = self.get_now_datetime()
        return datetime.datetime(now_datetime.year, now_datetime.month + 1,
                                 1) - datetime.timedelta(days=1)

    @classmethod
    def is_this_month(self, date, format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 指定时间是否在本周内
        :param date: 时间类型,支持timestamp/datetime/format_time
        :return 指定时间在本周内=True 指定时间不在本周内=False
        :last_editors: ChenXiaolei
        """
        compare_datetime = date
        if type(date) == int:
            compare_datetime = self.timestamp_to_datetime(date)
        elif type(date) == str:
            compare_datetime = self.format_time_to_datetime(date, format)
        if compare_datetime >= self.get_first_day_of_the_month(
        ) and compare_datetime <= self.get_last_day_of_the_month():
            return True
        return False

    @classmethod
    def get_first_day_of_the_year(self):
        """
        :Description: 获取本年第一天的日期
        :param 无
        :return datetime.date
        :last_editors: ChenXiaolei
        """
        now_datetime = self.get_now_datetime()
        return datetime.datetime(now_datetime.year, 1, 1)

    @classmethod
    def get_last_day_of_the_year(self):
        """
        :Description: 获取本年最后一天的日期
        :param 无
        :return datetime.date
        :last_editors: ChenXiaolei
        """
        now_datetime = self.get_now_datetime()
        return datetime.datetime(now_datetime.year + 1, 1,
                                 1) - datetime.timedelta(days=1)

    @classmethod
    def is_this_year(self, date, format='%Y-%m-%d %H:%M:%S'):
        """
        :Description: 指定时间是否在本年内
        :param date: 时间类型,支持timestamp/datetime/format_time
        :return 指定时间在本周内=True 指定时间不在本周内=False
        :last_editors: ChenXiaolei
        """
        compare_datetime = date
        if type(date) == int:
            compare_datetime = self.timestamp_to_datetime(date)
        elif type(date) == str:
            compare_datetime = self.format_time_to_datetime(date, format)
        if compare_datetime >= self.get_first_day_of_the_year(
        ) and compare_datetime <= self.get_last_day_of_the_year():
            return True
        return False