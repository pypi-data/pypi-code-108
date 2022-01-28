from __future__ import division
from ast import If
from re import I
import time
from unicodedata import name
import pandas as pd
from scipy.fft import ifft
import sys,os


import hbshare as hbs
from hbshare.db.simu import cons as ct
"""
@author: jingyang.dai
@contact: meng.lv@howbuy.com
@software: PyCharm
@file: corp.py
@time: 2020/9/18 9:59
"""



def get_prod_valuation_by_jjdm_gzrq(jjdm, gzrq, retry_count=3, pause=0.01, timeout=10):
    """
            根据基金代码、估值日期查询估值数据
        :param jjdm: 基金代码
        :param gzrq: 估值日期
        :return: jjdm 基金代码
                gzrq 估值日期
                kmdm 科目代码
                kmmc 科目名称   
                bz 币种
                hl 汇率
                sl 数量
                dwcb 单位成本
                cb 成本
                cbzjz 成本占净值 %
                hqssj 行情收市价(市价)
                sz 市值
                szzjz 市值占净值 %
                gzzz 估值增值
                tpxx 停牌信息
                qyxx 权益信息
        """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()
        # 测试环境
        # url = ct.HOWBUY_SIMU_GET_VALUATION_LIST_BY_JJDM_GZRQ % (
        #     ct.P_TYPE['http'], '192.168.220.107:8180', gzrq, jjdm)
        url = ct.HOWBUY_SIMU_GET_VALUATION_LIST_BY_JJDM_GZRQ % (
            ct.P_TYPE['http'], ct.DOMAINS['ams'], gzrq, jjdm)

        org_js = api.query(url)
        status_code = str(org_js['code'])
        if status_code != '0000':
            status = str(org_js['desc'])
            raise ValueError(status)

        if 'body' not in org_js:
            status = "未查询到估值信息"
            raise ValueError(status)

        data = org_js['body']
        prod_df = pd.DataFrame(data, columns=ct.HOWBUY_SIMU_VALUATION)
        # corp_df['tsname'] = corp_df['tsname'].astype(str)
        # corp_df['tsshortName'] = corp_df['tsshortName'].str.replace("#", "").str.replace("$", "").astype(str)
        # corp_df['tscode'] = corp_df['tscode'].astype(str)

        return prod_df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)


if __name__ == "__main__":
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    data = hbs.get_prod_valuation_by_jjdm_gzrq("S29494", "20150723")
    print(data)
