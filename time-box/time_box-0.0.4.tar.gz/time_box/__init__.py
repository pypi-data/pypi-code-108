#!/usr/bin/env python3
# coding = utf8
import datetime
import pytz
import time
import copy
import sys


def get_utc_datetime():
    """
    获取utc时间
    """
    utc_datetime_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return utc_datetime_str


def get_utc_timestamp():
    """
    获取utc时间的时间戳
    """
    utc_timestamp_str = datetime.datetime.utcnow().timestamp()
    return utc_timestamp_str


def get_utc_time_dict():
    """
    获取utc时间的时间和时间戳字典
    """
    utc_time_now = datetime.datetime.utcnow()
    utc_datetime_str = utc_time_now.strftime('%Y-%m-%dT%H:%M:%SZ')
    utc_timestamp_str = utc_time_now.timestamp()
    return {'utc_datetime_str': utc_datetime_str, 'utc_timestamp_str': utc_timestamp_str}


def get_year(
        date_input: str = None,  # 输入日期
        date_delimiter: str = "-"  # 日期分隔符
):
    """
    获取当前系统的当前时间：年份
    :return: 2018
    """
    if date_input is None:
        year = datetime.datetime.now().year
    else:
        a1 = date_input.find(date_delimiter, 0)
        year = int(date_input[0:a1])
    return year


def get_month(
        date_input: str = None,  # 输入日期
        date_delimiter: str = "-"  # 日期分隔符
):
    """
    获取当前系统的当前时间：月份
    :return: 8
    """
    if date_input is None:
        month = datetime.datetime.now().month
    else:
        date = str(date_input)
        a1 = date.find(date_delimiter, 0)
        a2 = date.find(date_delimiter, a1 + 1)
        month = int(date[a1 + 1:a2])
    return month


def get_day(
        date_input: str = None,  # 输入日期
        date_delimiter: str = "-"  # 日期分隔符
):
    """
    获取当前系统的当前时间：日数
    :return: 1
    """
    if date_input is None:
        day = datetime.datetime.now().day
    else:
        date = str(date_input)
        a1 = date.find(date_delimiter, 0)
        a2 = date.find(date_delimiter, a1 + 1)
        day = int(date[a2 + 1:len(date)])
    return day


def get_hour():
    """
    获取当前系统的当前时间：小时数（24小时制）
    :return: 14
    """
    hour = datetime.datetime.now().hour
    return hour


def get_minute():
    """
    获取当前系统的当前时间：分钟数
    :return: 28
    """
    minute = datetime.datetime.now().minute
    return minute


def get_second():
    """
    获取当前系统的当前时间：秒数
    :return: 23
    """
    second = datetime.datetime.now().second
    return second


def get_time():
    """
    获取当前系统的当前时间格式的时间，精确到秒且只有时间
    :return: 14:20:41
    """
    inner_now = datetime.datetime.now()
    data_time = inner_now.strftime('%H:%M:%S')
    return data_time


def get_datetime():
    """
    获取当前系统的当前时间格式的时间，精确到秒
    :return: 2018-08-01 14:18:31
    """
    inner_now = datetime.datetime.now()
    data_time = inner_now.strftime('%Y-%m-%d %H:%M:%S')
    return data_time


def get_datetime_full():
    """
    获取当前系统的当前时间格式的时间，精确度最高
    :return: 2018-08-01 14:16:50.611705
    """
    inner_now = datetime.datetime.now()
    return inner_now


def get_datetime_str_int():
    """
    获取当前系统的当前时间格式的时间，精确到秒
    :return: 20180801141831
    """
    inner_now = datetime.datetime.now()
    data_time = inner_now.strftime('%Y%m%d%H%M%S')
    return data_time


def get_relative_date(
        num: int = 0
):
    """
    获取当前系统当前时间的相对时间：日期，num为0表示当日，num为负数表示向历史推算的天数，num为正数表示向未来推算的天数
    :param num:
    :return: 2018-08-01
    """
    today = datetime.date.today()
    date = today - datetime.timedelta(days=-num)
    return date


def get_relative_datetime(
        num: int = 0
):
    """
    获取当前系统当前时间的相对时间：日期，num为0表示当日，num为负数表示向历史推算的天数，num为正数表示向未来推算的天数
    :param num:
    :return: 2021-04-23 17:23:27
    """
    today = datetime.datetime.now()
    date = today - datetime.timedelta(days=-num)
    return date.strftime('%Y-%m-%d %H:%M:%S')


def get_timestamp():
    """
    获取当前系统的当前时间戳格式的时间，返回的类型为int
    :return: 1533104393
    """
    inner_now = time.time()
    return int(inner_now)


def get_timestamp2datetime(
        timestamp: int,
        f: str = "%Y-%m-%d %H:%M:%S"
):
    """
    将时间戳转换为datetime时间
    :param timestamp: 同时支持字符串和数字格式
    :param f:
    :return: 2018-08-01 14:19:53
    """
    if timestamp is not None:
        time_array = time.localtime(timestamp)
        date_time = time.strftime(f, time_array)
        return date_time
    else:
        return


def get_timestamp2date(
        timestamp: int,
        f: str = "%Y-%m-%d"
):
    """
    将时间戳转换为datetime时间
    默认将输入转换为int
    :param timestamp:
    :param f:
    :return: 2018-08-01 14:19:53
    """
    if timestamp is not None:
        time_array = time.localtime(timestamp)
        date_time = time.strftime(f, time_array)
        return date_time
    else:
        return


def get_date2timestamp(
        date: str,
        f: str = "%Y-%m-%d"
):
    """
    将日期转换为对应日期的0点的时间戳
    :param date:
    :param f:
    :return: 1533052800
    """
    time_array = time.strptime(date, f)
    timestamp = int(time.mktime(time_array))
    return timestamp


def get_datetime2timestamp(
        data: str,
        f: str = "%Y-%m-%d %H:%M:%S"
):
    time_array = time.strptime(data, f)
    timestamp = int(time.mktime(time_array))
    return timestamp


def get_datetime2date(
        datetime_str: str
):
    datetime_timestamp = get_datetime2timestamp(datetime_str)
    date_str = get_timestamp2date(datetime_timestamp)
    return date_str


def timestamp_day_num_start(
        num: int = 0
):
    """
    换算出相对时间的当日开始时间的时间戳
    :param num:
    :return: 1533052800（2018-08-01 00:00:00）
    """
    inner = get_relative_date(num=num)
    return get_date2timestamp(str(inner))


def timestamp_day_num_end(
        num: int = 0
):
    """
    换算出相对时间的当日结束时间的时间戳
    :param num:
    :return: 1533139199（2018-08-01 23:59:59）
    """
    inner = get_relative_date(num=num+1)
    return get_date2timestamp(str(inner))-1


def get_format_date(
        date_ori: str,
        date_delimiter: str = '-',  # 日期分隔符号
):
    """
    将以'-'连接的字符串的日期格式化为日期格式
    :param date_ori:
    :param date_delimiter:
    :return: 2018-01-01
    """
    a1 = date_ori.find(date_delimiter, 0)
    a2 = date_ori.find(date_delimiter, a1+1)
    year = int(date_ori[0:a1])
    month = int(date_ori[a1+1:a2])
    day = int(date_ori[a2+1:len(date_ori)])
    format_date = datetime.date(year, month, day)
    return format_date


def get_format_date_2(
        date_ori: str
):
    """
    将以的字符串的日期格式化为日期格式:20200602
    按照位置分
    :param date_ori:
    :return: 2018-01-01
    """
    year = int(date_ori[0:4])
    month = int(date_ori[4:6])
    day = int(date_ori[6:8])
    format_date = datetime.date(year, month, day)
    return format_date


def get_format_datetime(
        datetime_ori: str,
        date_delimiter: str = '-',  # 日期分隔符号
        space_delimiter: str = " ",  # 空格分隔符号
        time_delimiter: str = ':'  # 时间分隔符号
):
    """
    将以'-'连接的字符串的日期格式化为日期格式
    :param datetime_ori:
    :param date_delimiter: 日期分隔符号
    :param space_delimiter: 空格分隔符号
    :param time_delimiter: 时间分隔符号
    :return: 2018-01-01
    """
    date_str, time_str = datetime_ori.split(space_delimiter)

    date_str = str(date_str)
    d1 = date_str.find(date_delimiter, 0)
    d2 = date_str.find(date_delimiter, d1+1)
    year_num = int(date_str[0:d1])
    month_num = int(date_str[d1+1:d2])
    day_num = int(date_str[d2+1:len(date_str)])

    time_str = str(time_str)
    t1 = time_str.find(time_delimiter, 0)
    t2 = time_str.find(time_delimiter, t1 + 1)
    hour_num = int(time_str[0:t1])
    minute_num = int(time_str[t1 + 1:t2])
    second_num = int(time_str[t2 + 1:len(time_str)])

    format_date = datetime.datetime(year_num, month_num, day_num, hour_num, minute_num, second_num)
    return format_date


def time_gap_seconds(
        start_time: str,
        end_time: str
):
    """
    计算两个时间的间隔秒数
    :param start_time:
    :param end_time:
    :return:
    """
    start_time_f = get_format_datetime(start_time)
    end_time_f = get_format_datetime(end_time)
    return (end_time_f - start_time_f).seconds


def time_gap_days(
        start_time: str,
        end_time: str
):
    """
    计算两个时间的间隔天数
    :param start_time:
    :param end_time:
    :return:
    """
    start_time_f = get_format_date(start_time)
    end_time_f = get_format_date(end_time)
    return (end_time_f - start_time_f).days


def get_add_date(
        date_input: str,
        num: int,
        f: str = '%Y-%m-%d'
):
    """
    计算指定日期（date_ori）的相对日期
    :param date_input:
    :param num:
    :param f:
    :return: 2018-01-02
    """
    date = get_format_date(date_input)
    delta = datetime.timedelta(days=num)
    n_days = date + delta
    date_add = n_days.strftime(f)
    return date_add


def get_timestamp_interval_seconds(
        timestamp: int
):
    """
    计算指定时间戳距离当前系统的当前时间的秒数，正数表示未来时间，负数表示过去时间
    :param timestamp:
    :return: 30830
    """
    inner_now = time.time()
    res = timestamp - int(inner_now)
    return res


def count_down(
        num: int
):
    """
    倒数计时器，按照指定的秒数原地倒计时刷新数字
    :param num:
    :return:
    """
    count = 0
    while count < num:
        n_count = num - count
        sys.stdout.write("\r%d " % n_count)
        sys.stdout.flush()
        time.sleep(1)
        count += 1


def running_controller(
        start_running_time: str,
        end_running_time: str,
        start_running_time_f: str = '%H:%M:%S',
        end_running_time_f: str = '%H:%M:%S'
):
    """
    判断系统时间是否落在设定的时间区间内，是则输出True，否则输出False
    :param start_running_time:
    :param end_running_time:
    :param start_running_time_f:
    :param end_running_time_f:
    :return:
    """
    if (start_running_time is None) and (end_running_time is None):
        return True
    else:
        inner_now = datetime.datetime.strptime(str(get_time()), "%H:%M:%S")
        inner_start = datetime.datetime.strptime(start_running_time, start_running_time_f)
        inner_end = datetime.datetime.strptime(end_running_time, end_running_time_f)

        if (inner_now >= inner_start) and (inner_now < inner_end):
            return True
        else:
            return False


def now():
    inner_now = datetime.datetime.now()
    return inner_now


def date_string(
        date=now()
):
    """
    将输入的时间转换为日期格式的字符串，如果不传入参数将取当前系统时间
    :param date:
    :return:
    """
    date_string_in = date.strftime('%Y-%m-%d')
    return date_string_in


def time_string(
        date=now()
):
    time_string_in = date.strftime('%Y-%m-%d %H-%M-%S')
    return time_string_in


def datetime_string(
        date=now()
):
    time_string_in = date.strftime('%Y-%m-%d %H-%M-%S')
    return time_string_in


def datetime_string_chs(
        date=now()
):
    time_string_in = date.strftime('%Y年%m月%d日%H时%M分%S秒')
    return time_string_in


def date_str_list(
        start_date: str,
        end_date: str
):
    # 生成起止时间之间的时间序列
    start_date_f = get_format_date(start_date)
    end_date_f = get_format_date(end_date)
    date_list = list()
    date_list.append(start_date_f)
    added_date = start_date_f
    while True:
        added_date = get_add_date(added_date, 1)
        added_date_f = get_format_date(added_date)
        if added_date_f > end_date_f:
            break
        else:
            date_list.append(str(added_date))
    return date_list


def date_str_list_form_now(
        day_num: int = 1
):
    start_date = get_add_date(date_string(), -day_num)
    end_date = date_string()
    res_list = date_str_list(start_date=start_date, end_date=end_date)
    return res_list


def get_normalized_date_string(
        days: int = 0
):
    """
    获取多少天以前的时间字符串
    :param days: 多少天以前
    :return: 时间字符串(xxxx-xx-xx xx:xx:xx)
    """
    current_time = datetime.datetime.now()
    target_time = current_time - datetime.timedelta(days=days)
    normalized_target_time = target_time.strftime('%Y-%m-%d %H:%M:%S')
    return normalized_target_time


def get_data_date_string(
        days: int = 0
):
    """
    获取多少天以前的时间字符串
    :param days: 多少天以前
    :return: 时间字符串(xxxx-xx-xx)
    """
    current_time = datetime.datetime.now()
    target_time = current_time - datetime.timedelta(days=days)
    date_time = target_time.strftime('%Y-%m-%d')
    return date_time


def get_date_string(
        days: int = 0
):
    """
    获取多少天以后的时间字符串
    :param days: 多少天以后，正数向未来计算，负数向历史计算，0是当天
    :return: 时间字符串(xxxx-xx-xx)
    """
    current_time = datetime.datetime.now()
    target_time = current_time + datetime.timedelta(days=days)
    date_str = target_time.strftime('%Y-%m-%d')
    return date_str


def time_day_num_start(
        num: int = 0
):
    """
    换算出相对时间的当日开始时间的时间
    :param num:
    :return: 2018-08-01 00:00:00
    """
    now = datetime.datetime.now()
    return now - datetime.timedelta(days=num, hours=now.hour, minutes=now.minute, seconds=now.second,
                                    microseconds=now.microsecond)


def time_day_num_end(
        num: int = 0
):
    """
    换算出相对时间的当日结束时间的时间
    :param num:
    :return: 2018-08-01 23:59:59
    """
    now = datetime.datetime.now()
    return now - datetime.timedelta(days=num - 1, hours=now.hour, minutes=now.minute, seconds=now.second + 1,
                                    microseconds=now.microsecond)


def timestamp_list_splitter(
        timestamp_list: list,
        n: int = 2
):
    # 时间戳范围拆分器
    """
    输入timestamp_list：[[start,end]]，splitter_num：2
    执行将list中的每段时间按照设定的份数拆分，拆分为粗略拆分，

    :return:
    """
    t_list_new = list()
    for each_t_list in timestamp_list:
        a = each_t_list[0]  # 获取开始时间戳
        b = each_t_list[1]  # 获取结束时间戳
        if (b - a) > 1:  # 当数字间隔大于1的时候才有拆分意义
            m = round((b - a)/n, 0)  # 计算加值数
            if m > 0:
                pass
            elif m == 0:
                m = 1
            else:
                continue
            t_list_new_temp = [[a, int(a + m)], [int(a + m + 1), b]]
            t_list_new.extend(t_list_new_temp)
        else:
            t_list_new.extend([each_t_list])
    return t_list_new


def date_gap_splitter(
        start_date: str,  # 开始日期
        end_date: str,  # 结束日期
        splitter_gap: int = 1,  # 拆分计算间隔
        successive: bool = False  # 结果是否连续
):
    """
    时间拆分器，将按照起止时间和间隔时间拆分时间段
    拆分从前向后拆分
    :return:
    """
    day_gap = time_gap_days(start_date, end_date)
    if splitter_gap >= day_gap:
        return [[start_date, end_date]]
    else:
        res_list = list()
        start_date_temp = start_date
        add_count = 0
        while True:
            end_date_temp = get_add_date(start_date_temp, splitter_gap)
            day_gap -= splitter_gap
            finish_num = get_date2timestamp(end_date) - get_date2timestamp(end_date_temp)
            if finish_num <= 0:
                res_list.append([str(start_date_temp), str(end_date)])
                break
            else:
                res_list.append([str(start_date_temp), str(end_date_temp)])
                if successive is True:
                    start_date_temp = copy.deepcopy(end_date_temp)
                else:
                    start_date_temp = get_add_date(end_date_temp, 1)
            add_count += 1
        return res_list


def get_time_duration(
        duration: int
):
    # 计算秒数的时长
    # start_duration = - 8 * 60 * 60  # 固定值
    temp_datetime = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=duration)
    # temp_datetime = get_timestamp2datetime(duration + start_duration)  # 计算1970-01-01 00：00：00 后指定秒的日期
    temp_date, temp_time = str(temp_datetime).split(' ')  # 分割日期和时间
    temp_day = time_gap_days(start_time='1970-01-01', end_time=temp_date)  # 计算天数间隔
    if temp_day == 0:
        duration_str = temp_time
    else:
        duration_str = '%sd %s' % (temp_day, temp_time)
    res = {
        'duration_days': temp_day,
        'duration_time': temp_time,
        'duration_str': duration_str,
        'duration': duration
    }
    return res


def print_t(
        text
):
    print("%s >> %s" % ((datetime.datetime.now()), text))


def utc_format(
        utc_time=None,
        timezone_local="Asia/shanghai",
        input_format="%Y-%m-%dT%H:%M:%S.%fZ",
        output_format="%Y-%m-%d %H:%M:%S"
):
    if utc_time is None:
        utc_time = datetime.datetime.utcnow()
    else:
        pass
    local_tz = pytz.timezone(timezone_local)
    if isinstance(utc_time, datetime.datetime) is True:
        utc_datetime = utc_time
    else:
        utc_datetime = datetime.datetime.strptime(utc_time, input_format)
    utc_timestamp = utc_datetime.timestamp()
    utc_datetime_str = utc_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    local_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
    local_timestamp = local_datetime.timestamp()
    local_datetime_str = local_datetime.strftime(output_format)
    res = {
        'utc_timestamp': int(utc_timestamp),
        'utc_timestamp_m': int(utc_timestamp * 1000),
        'utc_datetime_str': utc_datetime_str,
        'local_timestamp': int(local_timestamp),
        'local_timestamp_m': int(local_timestamp * 1000),
        'local_datetime_str': local_datetime_str,
    }
    return res


def get_file_name(
        date_delimiter: str = '-',  # 日期分隔符号
        space_delimiter: str = "+",  # 空格分隔符号
        time_delimiter: str = '-'  # 时间分隔符号
):
    """
    获取当前系统的当前时间格式的时间，精确到秒
    :return: 2018年08月01日 14时18分31秒
    """
    inner_now = datetime.datetime.now()
    f_list = ['%Y', date_delimiter, '%m', date_delimiter, '%d', space_delimiter, '%H', time_delimiter, '%M', time_delimiter, '%S']
    f_str = ''.join(f_list)
    data_time = inner_now.strftime(f_str)
    return data_time
