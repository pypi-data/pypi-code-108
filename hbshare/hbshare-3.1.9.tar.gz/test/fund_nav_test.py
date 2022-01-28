#!/usr/bin/python
#coding:utf-8

"""
@author: Meng.lv
@contact: meng.lv@howbuy.com
@software: PyCharm
@file: fund_nav_test.py
@time: 2020/6/15 10:50
"""
import os, sys
# 将hbshare根目录加入到环境变量
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import hbshare as hbs
import time

def test_get_fund_newest_nav():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    data = hbs.get_fund_newest_nav_by_code('000004')
    print(data)

def get_simu_corp_list_by_keyword():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    # data = hbs.get_simu_corp_list_by_keyword('黑石')
    data = hbs.get_prod_list_by_corp_code(80535346)
    print(data)


def get_simu_nav_by_code():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    data, total_count = hbs.get_simu_nav_by_code("P0010", "20190101", "20191231")
    print(data)
    print(total_count)

def get_prod_valuation_by_jjdm_gzrq():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    data = hbs.get_prod_valuation_by_jjdm_gzrq("S29494", "20150723")
    print(data)


def test_get_fund_holding():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    data = hbs.get_fund_holding('200016', '2020-09-30')
    print(data)

def get_fund_holding_publish_date():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    data = hbs.get_fund_holding_publish_date('200016')
    print(data)


def db_data_query():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")

    sql = "select JZRQ,JJDM,HBDR,HB1Z,HB1Y,HB3Y,HB6Y from funddb.jjhb t where t.jjdm = '020005' and t.JZRQ = '20090526'"
    data = hbs.db_data_query('readonly', sql)
    print(data)

def get_authorized_product_list():
    hbs.set_token("qwertyuisdfghjkxcvbn1000")
    mytoken ="..qRibJB_jTsGjtw3Anpua9n-"
    data = hbs.get_authorized_product_list(mytoken,'false','1000')
    print(data)


if __name__ == "__main__":
    data = hbs.db_data_query('highuser',"select  jjdm,max(jzrq) as jzrq from st_hedge.t_st_sm_qjzdhc where zblb='2106' and jzrq>='20211201' and jzrq<='20211231' and zbnp!=99999 group by jjdm",timeout=300)
    print(data)
    #test_get_fund_holding()


