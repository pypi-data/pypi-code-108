# -*- coding:utf-8 -*-

"""
获取基金净值数据接口
Created on 2020/6/15
@author: Meng Lv
@group: Howbuy FDC
@contact: meng.lv@howbuy.com
"""

from __future__ import division
import time
import pandas as pd
from hbshare.db.fund import cons as ct
import hbshare as hbs


def get_authorized_product_list(access_token,include_org='false',product_type='200', retry_count=3, pause=0.01, timeout=30):
    """
        获得公募基金最新净值（含最新回报，区间回报）
    :param access_token: 数据访问令牌
    :param include_org: 是否包含产品所属机构下所有产品
    :param product_type:产品类别
    :return:
    """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()
        url = ct.HOWBUY_RD_PROFUDUCT_PERMOISSIONS % (ct.P_TYPE['https'], ct.DOMAINS['ams'],
                                                     access_token,product_type,include_org)
        print(url)
        resp = api.query(url)
        status_code = resp['code']
        if status_code != '0000':
            status = str(resp['desc'] + ": 请确定是否有权限查询！")
            raise ValueError(status)

        if 'body' not in resp:
            status = "未查询到数据"
            raise ValueError(status)

        data = resp['body']
        fund_df = pd.DataFrame(data, columns=ct.HOWBUY_RD_PROFUDUCT_COLUMNS)

        fund_df['code'] = fund_df['code'].astype(str)
        fund_df['name'] = fund_df['name'].astype(str)
        fund_df['fullName'] = fund_df['fullName'].astype(str)
        fund_df['type'] = fund_df['type'].astype(str)
        fund_df['typeName'] = fund_df['typeName'].astype(str)

        return fund_df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)

