# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2019/6/24 11:23
# @Author: "John"
import datetime as dt
import time

from aliyun.log.getlogsrequest import GetLogsRequest


def query_log(client, query, project='java-crawler', log_store='reaper_log', query_start_time=0, query_end_time=0, line=100000):
    query_result = None

    while (not query_result) or (not query_result.is_completed()):
        rest = GetLogsRequest(project, log_store, query_start_time, query_end_time, "", query, reverse=True, line=line)
        query_result = client.get_logs(rest)

    return query_result.get_body()


def query_log_new(client, query, project='java-crawler', log_store='reaper_log', target_date=dt.datetime.today(), offset=1, line=100000):
    query_result = None

    # offset 大于0， 则往 target_date 前 offset 天查；否则往后查
    if offset > 0:
        query_start_obj = target_date - dt.timedelta(days=offset)
        query_end_obj = target_date - dt.timedelta(days=offset - 1)
    else:
        query_start_obj = target_date
        query_end_obj = target_date + dt.timedelta(days=1)

    # 查询开始的时间（转成时间戳）
    query_start = int(time.mktime(time.strptime(str(query_start_obj), '%Y-%m-%d')))
    # 查询结束的时间（转成时间戳）
    query_end = int(time.mktime(time.strptime(str(query_end_obj), '%Y-%m-%d')))

    while (not query_result) or (not query_result.is_completed()):
        rest = GetLogsRequest(project, log_store, query_start, query_end, "", query, reverse=True, line=line)
        query_result = client.get_logs(rest)

    return query_result.get_body()
