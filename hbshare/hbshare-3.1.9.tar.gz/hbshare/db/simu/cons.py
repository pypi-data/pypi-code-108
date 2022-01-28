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
DOMAINS = {'hbcgi': 'data.howbuy.com', 's': 's.howbuy.com','ams':'ams-data.intelnal.howbuy.com'}

##########################################################################
# 基金数据列名
HOWBUY_SIMU_CORP = ['tsname', 'tsshortName', 'tscode']
HOWBUY_SIMU_PROD_LIST = ['fundCode', 'fundName', 'hb1n','jjjz', 'jzrq', 'nhbdl', 'nhsyl']
HOWBUY_SIMU_NAV = ['jzrq', 'jjjz', 'ljjz','fqdwjz', 'jjjzStr', 'ljjzStr']
HOWBUY_SIMU_VALUATION = ['jjdm','gzrq','kmdm','kmmc','bz','hl','sl','dwcb','cb','cbzjz','hqssj','sz','szzjz','gzzz','tpxx','qyxx']

#test
##########################################################################
# 数据源URL
HOWBUY_SIMU_CORP_SEARCH = "%s%s/simu_searchdata_new.do?q=%s&fq=600&type=1"
HOWBUY_SIMU_GET_PROD_LIST_BY_CORP_CODE = "%s%s/cgi/simu/v634/company.json?jgdm=%s"
HOWBUY_SIMU_GET_NAV_LIST_BY_CODE = "%s%s/cgi/fund/historyfundnetvalueofpage.json?fundCode=%s&isPrivate=1&startDate=%s&endDate=%s&pageCount=%s&pageNum=%s"
# 私募估值信息
HOWBUY_SIMU_GET_VALUATION_LIST_BY_JJDM_GZRQ = "%s%s/data/query/guzhi/info?gzrq=%s&jjdm=%s"

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



TIME_SOLT = [("2000","前一周"),
            ("2007","近7天(1周）"),
            ("2014","近14天(2周)"),
            ("2028","近28天(4周)"),
            ("2101","近1月"),
            ("2102","近2月"),
            ("2103","近2月"),
            ("2106","近6月"),
            ("2118","近18月"),
            ("2201","近1年"),
            ("2202","近2年"),
            ("2203","近3年"),
            ("2205","近5年"),
            ("2210","近10年"),
            ("2998","今年以来"),
            ("2999","成立以来")]

TIME_DICT = {"DAY":"jzrq", "WEEK": "tjrq", "MONTH": "tjyf", "YEAR": "tjnf"}

def sql(k):
    key, dim_time = split_key(k)
    df = get_all_indexes()
    # print(df.loc["VOLATILITY"]['MONTH'])
    # print(df.index.isin(['VOLATILITY_RANK']))
    if dim_time not in list(TIME_DICT.keys()):
        raise KeyError(k ," 请检查时间维定义是否正确 ")

    if key not in df.index:
        raise KeyError(key ," 该指标不存在 ")

    if dim_time not in df.columns:
        raise KeyError(dim_time ," 配置中不存在该时间维度 ")

    if df.loc[key][dim_time] == "":
        raise KeyError(k, " 请和DB团队确认该指标是否计算!")

    print(str(df.loc[key]['NAME_CN']))
    return "select * from st_hedge."+str(df.loc[key][dim_time])+" a where a.jjdm ='%s' and "+ TIME_DICT[dim_time] + "='%s'"

def get_all_indexes():
    df = pd.read_csv("simu/simu.csv")
    df = df.set_index('KEY')
    #df = df.fillna(None)
    df = df.replace(np.nan, '', regex=True)
    return df

def split_key(k):
    last_idx = k.rfind("_")
    key = k[0:last_idx]
    dim_time = k[last_idx + 1:len(k)]
    return key, dim_time

def check_dim_time(k, dim_time):
    key, dt = split_key(k)

    df = get_all_indexes()
    # print(df.loc["VOLATILITY"]['MONTH'])
    # print(df.index.isin(['VOLATILITY_RANK']))
    if dt not in list(TIME_DICT.keys()):
        raise KeyError(k, " 请设置正确的时间维度格式 ")
    if dt == 'DAY' and len(dim_time) != 8:
        raise KeyError(dim_time, " 日频指标请确定时间维度格式：yyyymmdd ")
    if dt == 'WEEK' and len(dim_time) != 8:
        raise KeyError(dim_time, " 周频指标请确定时间维度格式：yyyymmdd ")
    if dt == 'MONTH' and len(dim_time) != 6:
        raise KeyError(dim_time, " 月频指标请确定时间维度格式：yyyymm ")
    if dt == 'YEAR' and len(dim_time) != 4:
        raise KeyError(dim_time, " 年度指标请确定时间维度格式：yyyy ")
