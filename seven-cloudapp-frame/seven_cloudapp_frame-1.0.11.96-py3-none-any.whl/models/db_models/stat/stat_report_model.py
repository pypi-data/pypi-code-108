# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 09:40:36
@LastEditTime: 2021-07-29 18:36:50
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class StatReportModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(StatReportModel, self).__init__(StatReport, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class StatReport:

    def __init__(self):
        super(StatReport, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.key_name = ""  # key名称
        self.key_value = 0  # key值
        self.create_day = 0  # 创建天
        self.create_month = 0  # 创建月
        self.create_year = 0  # 创建年
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'module_id', 'key_name', 'key_value', 'create_day', 'create_month', 'create_year', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "stat_report_tb"
