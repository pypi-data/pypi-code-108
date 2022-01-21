# -*- coding:utf-8 -*-
"""
Created on 2020/6/15
@author: Meng Lv
@group: Howbuy FDC
@contact: meng.lv@howbuy.com
"""
VERSION = '1.0.1'
P_TYPE = {'http': 'http://', 'ftp': 'ftp://', 'https': 'https://'}
FORMAT = lambda x: '%.2f' % x
FORMAT4 = lambda x: '%.4f' % x
DOMAINS = {'hbcgi': 'data.howbuy.com', 'static': 'static.howbuy.com','ams':'ams.howbuy.com'}

##########################################################################
# 基金数据列名
HOWBUY_FUND_NEWEST_NAV_COLUMNS = ['jjdm', 'jzrq', 'jjjz', 'ljjz', 'hbdr', 'hb1y',
                                  'hb3y', 'hb6y', 'hbjn', 'hb1n', 'zfxz']

HOWBUY_FUND_HOLDING_COLUMNS = ['zqdm', 'zqmc', 'zjbl', 'ccdb']

HOWBUY_RD_PROFUDUCT_COLUMNS = ['code', 'name', 'fullName', 'type','typeName']

#test
##########################################################################
# 数据源URL
HOWBUY_FUND_NEWEST_NAV = "%s%s/cgi/fund/navinfoquery.json?fundCode=%s"
HOWBUY_FUND_HOLDING = '%s%s/??/upload/auto/script/fund/data_%s.js?v=%s'

HOWBUY_RD_PROFUDUCT_PERMOISSIONS = "%s%s/admin/fof/pool/products/fund?access_token=%s&type=%s&org=%s"

##########################################################################
DATA_GETTING_TIPS = '[Getting data:]'
DATA_GETTING_FLAG = '#'
DATA_ROWS_TIPS = '%s rows data found.Please wait for a moment.'
DATA_INPUT_ERROR_MSG = 'date input error.'
NETWORK_URL_ERROR_MSG = '获取失败，请检查网络和URL'
DATE_CHK_MSG = '年度输入错误：请输入1989年以后的年份数字，格式：YYYY'
DATE_CHK_Q_MSG = '季度输入错误：请输入1、2、3或4数字'
TOP_PARAS_MSG = 'top有误，请输入整数或all.'
LHB_MSG = '周期输入有误，请输入数字5、10、30或60'

OFT_MSG = u'开放型基金类型输入有误，请输入all、equity、mix、bond、monetary、qdii'

DICT_NAV_EQUITY = {
    'fbrq': 'date',
    'jjjz': 'value',
    'ljjz': 'total',
    'change': 'change'
}

DICT_NAV_MONETARY = {
    'fbrq': 'date',
    'nhsyl': 'value',
    'dwsy': 'total',
    'change': 'change'
}

import sys
PY3 = (sys.version_info[0] >= 3)


def _write_head():
    sys.stdout.write(DATA_GETTING_TIPS)
    sys.stdout.flush()


def _write_console():
    sys.stdout.write(DATA_GETTING_FLAG)
    sys.stdout.flush()


def _write_tips(tip):
    sys.stdout.write(DATA_ROWS_TIPS % tip)
    sys.stdout.flush()


def _write_msg(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def _check_input(year, quarter):
    if isinstance(year, str) or year < 1989:
        raise TypeError(DATE_CHK_MSG)
    elif quarter is None or isinstance(quarter, str) or quarter not in [1, 2, 3, 4]:
        raise TypeError(DATE_CHK_Q_MSG)
    else:
        return True
