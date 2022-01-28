#!/usr/bin/python
#coding:utf-8
from __future__ import division
import time
from datetime import datetime
import pandas as pd
from hbshare.db.simu import cons as ct
import hbshare as hbs

"""
@author: Meng.lv
@contact: meng.lv@howbuy.com
@software: PyCharm
@file: nav.py.py
@time: 2020/9/18 9:18
"""


def get_simu_nav_by_code(code, start_date, end_date=datetime.now().strftime('%Y%m%d') , size=100, page=1, retry_count=3, pause=0.01, timeout=10):
    """
        根据基金代码查询历史净值、累计净值、复权单位净值(分页需要单独处理)
    :param code:
    :return:
    """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()

        url = ct.HOWBUY_SIMU_GET_NAV_LIST_BY_CODE % (ct.P_TYPE['https'], ct.DOMAINS['hbcgi'], code, start_date, end_date, size, page)

        org_js = api.query(url)
        status_code = int(org_js['common']['responseCode'])
        if status_code != 1:
            status = str(org_js['common']['responseContent'])
            raise ValueError(status)

        count = int(org_js['count'])

        if 'info' not in org_js:
            # status = "未查询到该基金数据"
            return pd.DataFrame([], columns=ct.HOWBUY_SIMU_NAV),0

        #['jzrq', 'jjjz', 'ljjz','fqdwjz', 'jjjzStr', 'ljjzStr']
        data = org_js['info']
        corp_df = pd.DataFrame(data, columns=ct.HOWBUY_SIMU_NAV)
        corp_df['jzrq'] = corp_df['jzrq'].astype(str)
        corp_df['jjjz'] = corp_df['jjjzStr'].str.replace("*", "").astype(float)
        corp_df['ljjz'] = corp_df['ljjzStr'].str.replace("*", "").astype(float)
        corp_df['fqdwjz'] = corp_df['fqdwjz'].str.replace("*", "").astype(float)
        corp_df['jzdw'] = corp_df['ljjz'].astype(float) / corp_df['jjjzStr'].str.replace("*", "").astype(float)

        corp_df = corp_df.drop('jjjzStr', axis=1)
        corp_df = corp_df.drop('ljjzStr', axis=1)
        return corp_df, count
    raise IOError(ct.NETWORK_URL_ERROR_MSG)