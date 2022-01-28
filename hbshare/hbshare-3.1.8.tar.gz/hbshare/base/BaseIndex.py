#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :BaseIndex.py
# @Time      :2021/4/25 4:49 下午
# @Author    :meng.lv
import hbshare as hbs
import pandas as pd
import numpy as np
import sys, os
from datetime import datetime, timedelta

class BaseIndex(object):

    def __init__(self, database, path):
        self.TIME_DICT = {"DAY": "jzrq", "WEEK": "tjrq", "MONTH": "tjyf", "YEAR": "tjnf"}
        self.database = database
        hbs.set_token("qwertyuisdfghjkxcvbn1000")
        self.config = self.init_config(path)

    def get_config(self):
        order = ['NAME_CN', 'KEY', 'DOMAIN', 'DAY', 'WEEK', 'MONTH', 'YEAR']
        return self.config[order]

    def call(self, sql):
        data = hbs.db_data_query(self.database, sql)
        if data['returnCode'] != 'F0000000':
            raise QueryException(data)
        return pd.DataFrame.from_dict(data['data'])

    def sql(self, k):
        key, dim_time = self.split_key(k)
        df = self.config
        if dim_time not in list(self.TIME_DICT.keys()):
            raise KeyError(k, " 请检查时间维定义是否正确 ")

        if key not in df.index:
            raise KeyError(key, " 该指标不存在 ")

        if dim_time not in df.columns:
            raise KeyError(dim_time, " 配置中不存在该时间维度 ")

        if df.loc[key][dim_time] == "":
            raise KeyError(k, " 请和DB团队确认该指标是否计算!")

        # print(str(df.loc[key]['NAME_CN']))
        return "select * from st_hedge." + str(df.loc[key][dim_time]) \
               + " a where a.jjdm ='%s' and " + self.TIME_DICT[dim_time] + "='%s'"

    def split_key(self, k):
        #first_idx = k.lfind("_")
        last_idx = k.rfind("_")
        #domain = k[0:first_idx]
        key = k[0:last_idx]
        dim_time = k[last_idx + 1:len(k)]
        return key, dim_time

    def check_dim_time(self, k, dim_time):
        key, dt = self.split_key(k)

        # df = self.get_all_config()
        # print(df.loc["VOLATILITY"]['MONTH'])
        # print(df.index.isin(['VOLATILITY_RANK']))
        if dt not in list(self.TIME_DICT.keys()):
            raise KeyError(k, " 请设置正确的时间维度格式 ")
        if dt == 'DAY' and len(dim_time) != 8:
            raise KeyError(dim_time, " 日频指标请确定时间维度格式：yyyymmdd ")
        if dt == 'WEEK' and len(dim_time) != 8:
            raise KeyError(dim_time, " 周频指标请确定时间维度格式：yyyymmdd ")
        if dt == 'MONTH' and len(dim_time) != 6:
            raise KeyError(dim_time, " 月频指标请确定时间维度格式：yyyymm ")
        if dt == 'YEAR' and len(dim_time) != 4:
            raise KeyError(dim_time, " 年度指标请确定时间维度格式：yyyy ")

        if dt == 'WEEK' and len(dim_time) == 8:
            tjrq = datetime.strptime(str(dim_time), "%Y%m%d")
            dim_time = datetime.strftime(tjrq - timedelta(tjrq.weekday()), "%Y%m%d")
        return dim_time


    def init_config(self, config_path):
        df = pd.read_csv(config_path)
        df['HBS_KEY'] = df['DOMAIN'] + "_" + df['KEY']
        df = df.set_index('HBS_KEY')
        # df = df.fillna(None)
        df = df.replace(np.nan, '', regex=True)
        return df
