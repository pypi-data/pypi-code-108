#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :db_data_save_test.py
# @Time      :2021/5/17 1:20 下午
# @Author    :meng.lv
import hbshare as hbs
import pandas as pd
import json

def handler_data(database, table_name, dt, keys, limit=1000):
    dt['M_OPT_TYPE'] = '01'
    dt.columns = dt.columns.str.upper()
    total = ( dt.shape[0] // limit  ) if dt.shape[0] % limit == 0 else dt.shape[0] // limit + 1
    for i in range(total):
        start = i * limit
        d = dt[ start : start + limit ]
        #print(d['commetrade'])
        json_data = json.loads(d.to_json(orient = 'records'))
        success = hbs.db_data_save(database, table_name, json_data, keys)

    # return success

tables = [
    {
        'table_name' : 'r_st_barra_factor_cov',
        'file_name' : 'factor_cov',
        'keys' : ['trade_date', 'factor_name'],
        'description' : '风险因子的协方差矩阵'
    },
    {
        'table_name' : 'r_st_barra_style_factor',
        'file_name' : 'style_factor',
        'keys' : ['trade_date', 'ticker'],
        'description' : '风险因子暴露表'
    },
    {
        'table_name' : 'r_st_barra_factor_return',
        'file_name' : 'factor_return',
        'keys' : ['trade_date', 'factor_name'],
        'description' : '风险因子收益率表'
    },
    {
        'table_name' : 'r_st_barra_specific_return',
        'file_name' : 'specific_return',
        'keys' : ['trade_date', 'ticker'],
        'description' : '个股的特异性收益表'
    },
    {
        'table_name' : 'r_st_barra_s_risk',
        'file_name' : 'specific_risk',
        'keys' : ['trade_date', 'ticker'],
        'description' : '个股的特异性风险'
    }
]


if __name__ == "__main__":
    if hbs.is_prod_env():
        print("tips: 当前运行环境为生产环境！")
    else:
        print("tips: 当前运行环境为非生产环境！")
    for tb in tables:
        data = pd.read_csv('/Users/meng.lv/Downloads/barra/'+ tb['file_name'] +'.csv', encoding='utf-8')
        s = hbs.db_data_save('stashare', tb['table_name'], data, tb['keys'])
        print(tb['description'])

# if __name__ == "__main__":
#     data = pd.read_csv('/Users/meng.lv/Downloads/factor_cov.csv', encoding='utf-8')
#     data.columns = data.columns.str.lower()
#     json_data = json.loads(data.to_json(orient='records'))
#     success = hbs.db_data_save('stashare','r_st_barra_factor_cov', json_data, ['trade_date', 'factor_name'])
#     print(success)
