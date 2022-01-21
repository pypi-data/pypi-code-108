#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/12 7:51 下午
# @Author  : lance.txl
# @Site    : 
# @File    : odps_utils.py
# @Software: PyCharm

from datetime import datetime,timedelta
from mq_utils.db_utils import DBDao
import requests
from pprint import pprint
class GetODPSData:
    def __init__(self,url):
        # 拼接时间和偏移量
        self.url = url
        self.db = DBDao()
    def set_db_params(self,host,user,password,database):
        self.db.set_params(host=host,user=user,password=password,database=database)
    def get_today(self):
        today = datetime.now().strftime("%Y%m%d")
        return today
    def get_yesterday(self):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        return yesterday.strftime("%Y%m%d")
    def get_before_yesterday(self):
        today = datetime.now()
        before_yesterday = today - timedelta(days=2)
        return before_yesterday.strftime("%Y%m%d")
    def get_response(self,url):
        r = requests.get(url)
        data = r.json()
        if not data or 'data' not in data:
            return None
        return data.get("data")
    def get_newest_queryodps(self,dt=""):
        if not dt:
            sql = "select dt,omit from get_odps_record order by id desc limit 1"
        else:
            sql = "select dt,omit from get_odps_record where dt=\"{}\" order by id desc limit 1".format(dt)
        l = self.db.execute_select_sql(sql)
        print(l)
        if l:
            return l[0]
        return l
    def insert_newest_queryodps(self,dt,omit):
        sql = "insert into get_odps_record(dt,omit) values (\"{}\",\"{}\")".format(dt,omit)
        self.db.execute_insert_sql(sql)

    def get(self):
        """
        调用获取2000条场所码数据
        @:param newest_data : (dt,omit)
        :return:
        """
        # 从数据库获取当前已经取的次数
        newest_data = self.get_newest_queryodps()
        dt = self.get_yesterday()
        omit = 0
        if newest_data:
            db_dt,db_omit = newest_data
            if db_dt == self.get_yesterday():
                omit = int(db_omit) + 1
        # 拼接url，获取到结果，归一化
        url = self.url.format(dt,omit)
        print(url)
        datas = self.get_response(url)
        pprint(datas)
        # 默认是获取昨天的数据，可能由于数据清洗过晚的缘故问题
        if not datas:
            # 补充获取前天的数据
            dt = self.get_before_yesterday()
            try_r = self.get_newest_queryodps(dt=dt)
            if not try_r:
                omit = 0
            else:
                omit = try_r[1]
            omit = int(omit) + 1
            url = self.url.format(dt, omit)
            print(url)
            datas = self.get_response(url)
        if not datas:
            # 取两天还是没有，直接返回
            return None
        self.insert_newest_queryodps(dt, omit)
        return datas
if __name__ == '__main__':
    pass

