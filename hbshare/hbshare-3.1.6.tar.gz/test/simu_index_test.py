#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :simu_index_test.py
# @Time      :2021/4/27 2:18 下午
# @Author    :meng.lv

import hbshare as hbs
import pandas  as pd
import time

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180)  # 设置打印宽度(**重要**)
    #data = hbs.simu_index("RISK_DOWNSIDE_WEEK","S00748", '20210423', ["2101"], show_log=False)

    #print(data)
    si = hbs.SimuIndex("RISK_MAX_DRAWDOWN_RANK_DAY",show_log=False)
    dt = si.get("S00748", '20210419', ["2101"])
    print(dt)
    cfg = si.get_config()
    indices = []
    for index, row in cfg.iterrows():
        if row['DAY']:
            indices.append((index+"_DAY","日频_"+row['NAME_CN']))
        if row['WEEK']:
            indices.append((index+"_WEEK","周频_"+row['NAME_CN']))
        if row['MONTH']:
            indices.append((index+"_MONTH","月频_"+row['NAME_CN']))
        if row['YEAR']:
            indices.append((index+"_YEAR","年频_"+row['NAME_CN']))
    print(indices)
    # sql = "select JZRQ,JJDM,HBDR,HB1Z,HB1Y,HB3Y,HB6Y from funddb.jjhb t where t.jjdm = '020005' and t.JZRQ = '20090526'"
    # data = hbs.db_data_query('readonly', sql)
    # print(data)

