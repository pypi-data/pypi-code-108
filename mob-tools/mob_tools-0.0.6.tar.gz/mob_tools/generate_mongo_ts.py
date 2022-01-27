# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2019/10/17 17:52
# @Author: "John"
import time

import pymongo

import bson
import os
import shutil
import sys
import traceback
from datetime import datetime, timedelta

import requests
from pymongo import MongoClient

"""
    模板作用： 
        1、main_function 这个方法，提供对指定《数据库》中的指定《表》进行循环查询，将查询出来的 document，传递到 core_logic 中进行处理
        2、core_logic 这个方法由调用 data_fix_main 的用户自己完成，必须有三个参数；
        3、本模板，可以通过 pip install zy-tools 直接调用，不必拷贝过来拷贝过去
"""


# 只需传入文件名称，自动生成以当前脚本名称为前缀的 .txt 文件，保存到相对路径下，作为日志文件。
def process_logger(msg, fl_name='', mode="a", need_time=True, need_log=True):
    if not need_log:
        return

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger_file_name = os.path.basename(sys.argv[0])[:-3] + fl_name + ".log"
    with open(logger_file_name, mode) as f:
        if need_time:
            f.write(time_str + ' => ')
        f.write(msg)
        f.write("\n")


# 获取文件最后一个合法的 _id，用于断点续读
def get_last_id(file_name):
    with open(file_name, 'r') as f:

        index = -1
        while True:
            _id = f.readlines()[index].strip()
            if len(_id) == 24:
                return _id

            process_logger(f"Get the {-index} th _id error; Current _id: {_id}")
            index -= 1


def find_documents(conn, data_base, collection, query, projection, sort_key="_id", sort_value=pymongo.ASCENDING, limits=0):
    # 默认根据_id 升序排列，不限制返回的结果数量
    _docs = conn[data_base][collection].find(query, projection).sort(sort_key, sort_value).limit(limits)
    # 将结果集放到一个 list 中，方便计数
    docs = [item for item in _docs]
    return docs


def core_logic_example(conn, document, is_sandbox):
    """
    核心处理逻辑样例，调用者自己实现。
    【注意】必须有且仅有这三个参数

    :param conn:
    :param document:
    :param is_sandbox:
    :return:
    """
    pass


def generate_mongo_ts(uri, db, collection, more_filter, projections, core_logic, start_id='', end_id='', limits=500, need_stream_process=False, **kwargs):
    """

    :param uri: mongoDB 地址
    :param db: mongoDB 库名
    :param collection: mongoDB 表名
    :param more_filter: 其他 query
    :param projections: projection
    :param core_logic: 核心处理逻辑，调用方自行提供
    :param start_id: 自定义查询起点，必须是 MongoDB 的 ObjectId
    :param end_id: 自定义查询终点，必须是 MongoDB 的 ObjectId
    :param limits: 查询 MongoDB 的 limit
    :param need_stream_process: 是否需要流处理，true 的话，则由核心处理逻辑处理每次查询出来的所有记录；默认为 false，逐条处理
    :return:
    """
    query = {}
    current_id = ''
    exception_count = 0
    has_query_count = 0
    has_read_id_count = 0
    exit_after_some_time_initialed = False
    exit_after_some_time = datetime(2099, 12, 31)

    if isinstance(uri, str):
        conn = MongoClient(uri)
    elif isinstance(uri, pymongo.mongo_client.MongoClient):
        conn = uri
    else:
        process_logger(f'uri 类型错误，系统退出。')
        sys.exit('uri 类型错误')

    # 传入起点，则以传入的 objectId 为起点，否则以库中查询的第一条或者读取本地文件。
    if start_id:
        query = {"_id": {"$gte": bson.ObjectId(start_id)}}

    if more_filter:
        query.update(more_filter)

    # 捕获异常20 次，则退出检查
    while exception_count < 20:

        """
            如果需要动态控制调度产生的速度，需要调用方提供一个方法
            - 在调用 generate_mongo_ts 时，以关键词参数的形式传递进来。关键词的 key 必须是 need_wait_for_consumer
            - 该方法不能传递参数，且返回值必须是 Bool；
            - 返回值为 False 表示无需等待，继续产生调度；
            - 返回值为 True  表示需要等待，每 10 秒钟请求一次该方法，根据返回结果判断是否继续等待
        """

        if kwargs and 'need_wait_for_consumer' in kwargs.keys():

            need_wait_for_consumer = kwargs.get('need_wait_for_consumer')

            is_need_wait_for_consumer = need_wait_for_consumer()

            assert isinstance(is_need_wait_for_consumer, bool), "params need to be bool"

            while is_need_wait_for_consumer:
                # 为了保持链接， 10 秒查询一次数据库
                for i in range(60):
                    time.sleep(10)
                    conn.enterprise.Counters.find_one({'seq': 736564644})
                    is_need_wait_for_consumer = need_wait_for_consumer()
                    if not is_need_wait_for_consumer:
                        break

                    process_logger(f'queue size is greater than limit, sleep ten minus to wait for consumer, retry time: {i}.')

        has_query_count += 1
        docs = find_documents(conn, db, collection, query, projections, "_id", pymongo.ASCENDING, limits)
        fl = "_query_db_counts"
        log_msg = f"****** Has queried {collection} with {query}: {has_query_count}*{limits}={has_query_count * limits}  documents. *******"
        process_logger(log_msg, fl_name=fl, mode="w")

        try:
            # 查询结果为空，根据情况判断是否直接退出
            if not docs:
                if kwargs and "not_exit_when_at_end" in kwargs.keys():

                    # 当查询某个 MongoDB 达到终点，判断是否直接退出
                    not_exit_when_at_end = kwargs.get("not_exit_when_at_end")
                    # 当查询某个 MongoDB 达到终点，等待时间(单位分钟)
                    wait_producer_minute = kwargs.get('wait_producer_minute')

                    """
                        当MongoDB查询到终点时
                        - 如果调用方给定 not_exit_when_at_end=true，则表示不允许直接退出。有两种情况
                        -- 1、not_exit_when_at_end=true，wait_producer_time=xx（分钟），则要求 xx 分钟内继续尝试请求，实时后还是没有值的话，则退出
                    """
                    if not_exit_when_at_end and (exit_after_some_time > datetime.now()):

                        if not exit_after_some_time_initialed:

                            if wait_producer_minute:
                                assert isinstance(wait_producer_minute, int), "wait_producer_time need to be int(minute) type"
                                exit_after_some_time = datetime.now() + timedelta.min(wait_producer_minute)
                            else:
                                exit_after_some_time = datetime.now() + timedelta.min(60)

                            exit_after_some_time_initialed = True

                        process_logger(f'At the end of mongo docs, sleep 10 seconds and re check mongo again, final exit time: {exit_after_some_time}, Last _id is: {current_id}')
                        # 设置退出时间内，每 10 秒钟检查一下 MongoDB
                        time.sleep(10)
                        continue
                    else:
                        process_logger(f"Still empty doc after wait some time, exit! Final exit time: {exit_after_some_time}; Last _id is: {current_id}.")
                        return
                else:
                    process_logger(f"Empty doc, exit! Last _id is: {current_id}.")
                    return

            # 需要将所有 docs 一起处理
            if need_stream_process:

                '''
                    程序走到这里，说明MongoDB还能查到数据作为下一轮调度，
                    需要重置 exit_after_some_time_initialed = False
                '''
                exit_after_some_time_initialed = False

                current_id = _id = docs[-1].get("_id")
                query["_id"] = {"$gt": current_id}
                # 防止杀死进程的时候，这一轮没有执行完毕，下一次执行的时候会丢失数据
                process_logger(str(docs[0].get("_id")), fl_name=f'_has_read_{collection}_ids', mode='w', need_time=False)
                core_logic(conn, docs)
                # 程序退出条件
                if end_id:
                    real_end_id = None
                    if isinstance(end_id, str):
                        real_end_id = bson.ObjectId(end_id)
                    elif isinstance(end_id, bson.ObjectId):
                        real_end_id = end_id
                    if current_id > real_end_id:
                        process_logger(f"Get end point, and mission is over! Last _id is: {current_id}.")
                        sys.exit()
                continue

            for doc in docs:
                has_read_id_count += 1
                current_id = _id = doc.get("_id")
                query["_id"] = {"$gt": current_id}
                process_logger(str(current_id), fl_name=f'_has_read_{collection}_ids', mode='w', need_time=False)

                # 程序退出条件
                if end_id:
                    real_end_id = None
                    if isinstance(end_id, str):
                        real_end_id = bson.ObjectId(end_id)
                    elif isinstance(end_id, bson.ObjectId):
                        real_end_id = end_id
                    if current_id > real_end_id:
                        process_logger(f"Get end point, and mission is over! Last _id is: {current_id}.")
                        sys.exit()

                # 核心处理逻辑
                core_logic(conn, doc)

        except Exception as e:
            query["_id"] = {"$gt": current_id}  # 新的query
            process_logger(f'Get error, exception msg is {str(e) + ",trace:" + traceback.format_exc()}, current _id is: {current_id}.')
            exception_count += 1

    process_logger(f"Catch exception 20 times, mission is over. Last _id is: {current_id}.")
