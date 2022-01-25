#!/usr/bin/python
#coding:utf-8
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime


# 数据库参数配置
engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
    'admin', 'mysql', '192.168.223.152', '3306', 'riskmodel'))

# 经济宏观数据入库
data = pd.read_excel('D:\\kevin\\数据汇总.xlsx', sheet_name=0).rename(
    columns={"日期": "trade_date", "经济增长": "economy_increase"})
data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
data.to_sql('macro_economy', engine, index=False, if_exists='append')

# 市场宏观数据入库
data = pd.read_excel('D:\\kevin\\数据汇总.xlsx', sheet_name=1).rename(
    columns={"日期": "trade_date", "万德全A": "wind_A", "沪深300": "HS300", "中证500": "ZZ500"})
data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
data.to_sql('market_macro', engine, index=False, if_exists='append')

# 市场微观数据入库
data1 = pd.read_excel("D:\\kevin\\数据汇总.xlsx", sheet_name=2).rename(
    columns={"日期": "trade_date", "万德全A": "wind_A", "沪深300": "HS300", "中证500": "ZZ500"})
data1['trade_date'] = data1['trade_date'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
data1['direction'] = 'left'
data2 = pd.read_excel("D:\\kevin\\数据汇总.xlsx", sheet_name=3).rename(
    columns={"日期": "trade_date", "万德全A": "wind_A", "沪深300": "HS300", "中证500": "ZZ500"})
data2['trade_date'] = data2['trade_date'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
data2['direction'] = 'right'
data = pd.concat([data1, data2])
data.to_sql('market_micro', engine, index=False, if_exists='append')
