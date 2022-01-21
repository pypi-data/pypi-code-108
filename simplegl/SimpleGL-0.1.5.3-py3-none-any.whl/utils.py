# -*- coding: utf-8 -*- 
# @Time : 9/29/21 10:04 AM 
# @Author : mxt
# @File : utils.py
from datetime import datetime


def time_format(source_time: str = ""):
    _time = source_time.replace("T", " ").replace(".", " ").split(" ")
    return " ".join(_time[:-1])


def get_time_diff(created_at: str = "1949-10-01 00:00:00"):
    create_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    time_diff = (datetime.today() - create_time).total_seconds()
    if int(abs(time_diff) / 60) < 1 and time_diff < 0:
        return f"{int(abs(time_diff))}秒后"
    elif int(abs(time_diff) / 60 / 60) < 1 and time_diff < 0:
        return f"{int(abs(time_diff) / 60)}分钟后"
    elif int(abs(time_diff) / 60 / 60 / 24) < 1 and time_diff < 0:
        return f"{int(abs(time_diff) / 60 / 60)}小时后"
    elif int(abs(time_diff) / 60 / 60 / 24) >= 1 and time_diff < 0:
        return f"{int(abs(time_diff) / 60 / 60 / 24)}天后"
    elif int(time_diff / 60) < 1:
        return f"{int(time_diff)}秒前"
    elif int(time_diff / 60 / 60) < 1:
        return f"{int(time_diff / 60)}分钟前"
    elif int(time_diff / 60 / 60 / 24) < 1:
        return f"{int(time_diff / 60 / 60)}小时前"
    elif int(time_diff / 60 / 60 / 24) >= 1:
        return f"{int(time_diff / 60 / 60 / 24)}天前"
