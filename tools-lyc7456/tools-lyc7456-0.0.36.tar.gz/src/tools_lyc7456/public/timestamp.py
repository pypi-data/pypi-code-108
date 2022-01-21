import datetime


# 假设此刻时间是 2021-07-07 17:04:15.889853
def getStrfTime(diff_day=0, timeformat_type='day'):
    """获取格式化的时间戳

    Args:
        diff_day (int, optional): 间隔时间差天数. Defaults to 0.
        timeformat_type (str, optional): 要返回的时间戳格式. Defaults to 'day'.
                        可选参数：(
                        'year' 2021 | 
                        'month' 202107 | 
                        'month_num' 7 | 
                        'day' 20210707 | 
                        'hour' 2021070717 | 
                        'min' 202107071704 |
                        'second' 20210707170415)

    Returns:
        [str]: 返回字符串类型的时间戳
    """
    now = datetime.datetime.now()
    if timeformat_type == 'year':
        timeformat_x = (now + datetime.timedelta(days=diff_day)).strftime("%Y")
    elif timeformat_type == 'month':
        timeformat_x = (now +
                        datetime.timedelta(days=diff_day)).strftime("%Y%m")
    elif timeformat_type == 'month_num':
        timeformat_x = str(
            int((now + datetime.timedelta(days=diff_day)).strftime("%m")))
    elif timeformat_type == 'day':
        timeformat_x = (now +
                        datetime.timedelta(days=diff_day)).strftime("%Y%m%d")
    elif timeformat_type == 'hour':
        timeformat_x = (now +
                        datetime.timedelta(days=diff_day)).strftime("%Y%m%d%H")
    elif timeformat_type == 'min':
        timeformat_x = (
            now + datetime.timedelta(days=diff_day)).strftime("%Y%m%d%H%M")
    elif timeformat_type == 'second':
        timeformat_x = (
            now + datetime.timedelta(days=diff_day)).strftime("%Y%m%d%H%M%S")

    return timeformat_x




