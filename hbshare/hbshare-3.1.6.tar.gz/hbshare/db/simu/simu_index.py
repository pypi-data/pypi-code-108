#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :HighDataIndex.py
# @Time      :2021/4/25 3:52 下午
# @Author    :meng.lv

from hbshare.base import BaseIndex
from hbshare.db.simu import cons as ct
import os, sys
"""
 私募指标
"""

class SimuIndex(BaseIndex.BaseIndex):

    def __init__(self, key, show_log=False):
        path = os.path.abspath(os.path.dirname(__file__)) + "/simu.csv"
        super(SimuIndex, self).__init__("highuser", path)
        self.key = key
        self.show_log = show_log
        self.sql = super(SimuIndex, self).sql(self.key)
        self.print_msg(self.sql)

    def set_key(self, key):
        self.key = key
        self.sql = super(SimuIndex, self).sql(self.key)
        self.print_msg(self.sql)

    def print_msg(self, msg):
        if self.show_log:
            print("Output:",msg)

    def get(self, jjdm, time_dim_val, time_solt=None, benchmark=None):
        #检查时间格式
        time_dim_val = super(SimuIndex, self).check_dim_time(self.key, time_dim_val)
        l_sql = self.sql % (jjdm, time_dim_val)
        self.print_msg(l_sql)
        data = super(SimuIndex, self).call(l_sql)
        if time_solt != None:
            data = data.drop(index=data[~data['zblb'].isin(time_solt)].index.tolist())

        if benchmark != None:
            data = data.drop(index=data[~data['jzdm'].isin(benchmark)].index.tolist())
        return data

def simu_index(key, jjdm, dim_time, time_solt=None, benchmark=None, show_log=True):
    simuIdx = SimuIndex(key, show_log)
    return simuIdx.get(jjdm, dim_time, time_solt)

