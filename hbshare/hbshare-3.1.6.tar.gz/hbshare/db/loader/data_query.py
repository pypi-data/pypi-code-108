#!/usr/bin/python
#coding:utf-8

"""
@author: Meng.lv
@contact: meng.lv@howbuy.com
@software: PyCharm
@file: data_query.py
@time: 2021/1/20 8:44
"""
import time
import hbshare as hbs
from hbshare.db.fund import cons as ct


def db_data_query(db, sql, page_size=1000, page_num=1, is_pagination=True, retry_count=3, pause=0.01, timeout=300):
    """
        通用DB数据查询接口
    :param db: 数据库名（readonly(ORACLE库), alluser(MYSQL库), smpp(SMPP库)）
    :param sql: 执行脚本
    :param page_size: 每页大小
    :param page_num: 当前页码
    :param is_pagination: 是否分页
    :param retry_count: 重试次数
    :param pause: 重试间隔时间
    :param timeout: 超时时间 (0,600]
    :return:
    """
    api = hbs.hb_api(timeout=timeout)
    for _ in range(retry_count):
        time.sleep(pause)
        #ct._write_console()
        url = "http://fpc-data.intelnal.howbuy.com/data/query/commonapi?dataTrack=%s" % (time.time())
        post_body = {
                "database": db,
                "sql": sql,
                "ifByPage": is_pagination,
                "pageNum": page_num,
                "pageSize": page_size
        }
        data = api.query(url, 'post', post_body)
        success = data['success']
        if success != 1:
            status = str(data['returnCode'])+":"+str(data['returnMsg'])
            raise ValueError(status)
        # data_frame = pd.DataFrame(data['data'])
        # pagination = {
        #     "pageNum": page_num,
        #     "pageSize": page_size,
        #     "total": int(data['total']),
        #     "pages": int(data['pages'])
        # }
        return data
    raise IOError(ct.NETWORK_URL_ERROR_MSG)

