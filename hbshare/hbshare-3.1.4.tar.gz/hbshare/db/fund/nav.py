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
import demjson


def get_fund_newest_nav_by_code(code, retry_count=3, pause=0.01, timeout=10):
    """
        获得公募基金最新净值（含最新回报，区间回报）
    :param code:
    :return:
    """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()
        url = ct.HOWBUY_FUND_NEWEST_NAV % (ct.P_TYPE['https'], ct.DOMAINS['hbcgi'], code)

        org_js = api.query(url)
        status_code = int(org_js['common']['responseCode'])
        if status_code != 1:
            status = str(org_js['common']['responseContent'])
            raise ValueError(status)

        if 'opens' not in org_js:
            status = "未查询到该基金数据"
            raise ValueError(status)

        data = org_js['opens']
        fund_df = pd.DataFrame(data, columns=ct.HOWBUY_FUND_NEWEST_NAV_COLUMNS)
        fund_df['jjjz'] = fund_df['jjjz'].astype(float)
        fund_df['ljjz'] = fund_df['ljjz'].astype(float)
        fund_df['hbdr'] = fund_df['hbdr'].astype(float)
        fund_df['hb1y'] = fund_df['hb1y'].astype(float)
        fund_df['hb3y'] = fund_df['hb3y'].astype(float)
        fund_df['hb6y'] = fund_df['hb6y'].astype(float)
        fund_df['hbjn'] = fund_df['hbjn'].astype(float)
        fund_df['hb1n'] = fund_df['hb1n'].astype(float)
        fund_df['zfxz'] = fund_df['zfxz'].astype(float)
        return fund_df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)


def get_fund_holding(fund_code, publish_date, retry_count=3, pause=0.01):
    """
        获得公募基金持仓情况
    :param fund_code: 基金代码
    :param publish_date: 公告日期
    :param retry_count: 重试次数
    :param pause: 重试间隔时间
    :return:
    """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()
        url = ct.HOWBUY_FUND_HOLDING % (ct.P_TYPE['https'], ct.DOMAINS['static'], fund_code, time.time())

        js_text = api.get(url)
        gpzh = js_text.splitlines()[6].replace(";", "")[15:]

        # 日期格式转化
        # st = time.strftime("%Y-%m-%d", time.strptime(publish_date, "%Y%m%d"))

        holding = demjson.decode(gpzh)[publish_date]

        fund_df = pd.DataFrame(holding, columns=ct.HOWBUY_FUND_HOLDING_COLUMNS)
        fund_df['zqdm'] = fund_df['zqdm'].astype(str)
        fund_df['zqmc'] = fund_df['zqmc'].astype(str)
        fund_df['zjbl'] = fund_df['zjbl'].astype(float)
        fund_df['ccdb'] = fund_df['ccdb'].astype(float)
        return fund_df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)


def get_fund_holding_publish_date(fund_code, retry_count=3, pause=0.01):
    """
        获得公募基金定期报告发布时间查询
    :param fund_code: 基金代码
    :param retry_count: 重试次数
    :param pause: 重试间隔时间
    :return:
    """
    api = hbs.hb_api()
    for _ in range(retry_count):
        time.sleep(pause)
        ct._write_console()
        url = ct.HOWBUY_FUND_HOLDING % (ct.P_TYPE['https'], ct.DOMAINS['static'], fund_code, time.time())

        js_text = api.get(url)
        gpzh = js_text.splitlines()[6].replace(";", "")[15:]

        date_list = demjson.decode(gpzh)["dateList"]

        fund_df = pd.DataFrame(date_list, columns=['publish_date'])
        fund_df['publish_date'] = fund_df['publish_date'].astype(str)
        return fund_df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)
