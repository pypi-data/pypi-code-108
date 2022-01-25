#!/usr/bin/python
#coding:utf-8
from __future__ import division
import time
import pandas as pd
from hbshare.db.simu import cons as ct
import hbshare as hbs

"""
@author: Meng.lv
@contact: meng.lv@howbuy.com
@software: PyCharm
@file: corp.py
@time: 2020/9/18 9:59
"""


def get_simu_corp_list_by_keyword(keyword, retry_count=3, pause=0.01, timeout=10):
    """
        根据关键字查询私募机构管理人列表
    :param code:
    :return:
    """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()
        url = ct.HOWBUY_SIMU_CORP_SEARCH % (ct.P_TYPE['https'], ct.DOMAINS['s'], keyword)

        org_js = api.query(url)
        total_count = int(org_js['totalCount'])

        if 'smgsContent' not in org_js:
            status = "未查询到数据"
            raise ValueError(status)

        data = org_js['smgsContent']
        corp_df = pd.DataFrame(data, columns=ct.HOWBUY_SIMU_CORP)
        corp_df['tsname'] = corp_df['tsname'].astype(str)
        corp_df['tsshortName'] = corp_df['tsshortName'].str.replace("#", "").str.replace("$", "").astype(str)
        corp_df['tscode'] = corp_df['tscode'].astype(str)

        return corp_df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)


def get_prod_list_by_corp_code(corp_code, retry_count=3, pause=0.01, timeout=10):
    """
            根据私募机构管理人代码查询机构管理的产品列表
        :param code:
        :return:
        """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()
        url = ct.HOWBUY_SIMU_GET_PROD_LIST_BY_CORP_CODE % (ct.P_TYPE['https'], ct.DOMAINS['hbcgi'], corp_code)

        org_js = api.query(url)
        status_code = str(org_js['code'])
        if status_code != '0000':
            status = str(org_js['desc'])
            raise ValueError(status)

        if 'gljjList' not in org_js['body']:
            status = "未查询到该公司管理产品数据"
            raise ValueError(status)

        data = org_js['body']['gljjList']
        prod_df = pd.DataFrame(data, columns=ct.HOWBUY_SIMU_PROD_LIST)
        # corp_df['tsname'] = corp_df['tsname'].astype(str)
        # corp_df['tsshortName'] = corp_df['tsshortName'].str.replace("#", "").str.replace("$", "").astype(str)
        # corp_df['tscode'] = corp_df['tscode'].astype(str)

        return prod_df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)