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
import json


def db_data_save_raw(database, table_name,  data=[], private_key=[], retry_count=1, pause=0.01, timeout = 300):
    """
        通用DB数据保存接口
    :param database: 数据库名（不支持ORACLE库,支持(MYSQL)库: stfund(公募产品库),
            stportfolio(组合产品库),sthedge(私募产品库), stfixed(固收产品库),
            stmarket(市场指数库),stashare(市场股票库), stinsurance(保险产品库), stmain(公共库)
    :param table_name: 执行脚本
    :param data: 数据
    :param private_key: 业务主键
    :param retry_count: 重试次数
    :param pause: 重试间隔时间
    :param timeout: 超时时间 (0,600]
    :return:
    """
    api = hbs.hb_api(timeout=timeout)
    for _ in range(retry_count):
        time.sleep(pause)
        #ct._write_console()
        if hbs.is_prod_env():
            url = "http://fpc-data.intelnal.howbuy.com/data/modify/commonapi?dataTrack=%s" % (time.time())
        else:
            url = "http://192.168.223.48:8101/data/modify/commonapi?dataTrack=%s" % (time.time())
        post_body = {
                "database": database,
                "tableName": table_name,
                "privateKey": private_key
        }
        post_body["dataList"] = data
        data = api.query(url, 'post', post_body)
        # print(post_body)
        success = data['success']
        if not success:
            status = str(data['returnCode'])+":"+str(data['returnMsg'])
            raise ValueError(status)
        # data_frame = pd.DataFrame(data['data'])
        # pagination = {
        #     "pageNum": page_num,
        #     "pageSize": page_size,
        #     "total": int(data['total']),
        #     "pages": int(data['pages'])
        # }
        return success
    raise IOError(ct.NETWORK_URL_ERROR_MSG)

def db_data_save(database, table_name, dt, keys, limit=1000):
    """
            通用DB数据保存接口
        :param database: 数据库名（不支持ORACLE库,支持(MYSQL)库: stfund(公募产品库),
                stportfolio(组合产品库),sthedge(私募产品库), stfixed(固收产品库),
                stmarket(市场指数库),stashare(市场股票库), stinsurance(保险产品库), stmain(公共库)
        :param table_name: 执行脚本
        :param dt: 数据
        :param keys: 业务主键
        :return:
    """
    ret = True
    dt['M_OPT_TYPE'] = '01'
    dt.columns = dt.columns.str.upper()
    total = ( dt.shape[0] // limit  ) if dt.shape[0] % limit == 0 else dt.shape[0] // limit + 1
    for i in range(total):
        start = i * limit
        d = dt[ start : start + limit ]
        #print(d['commetrade'])
        json_data = json.loads(d.to_json(orient = 'records'))
        success = db_data_save_raw(database, table_name, json_data, keys)
        if not success:
            print("there are some error", d)
        ret = ret and success
    return ret