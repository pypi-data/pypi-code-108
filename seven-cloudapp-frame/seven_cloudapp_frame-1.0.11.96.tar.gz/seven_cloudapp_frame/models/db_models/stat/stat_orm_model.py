# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 09:40:36
@LastEditTime: 2021-09-10 16:11:30
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class StatOrmModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(StatOrmModel, self).__init__(StatOrm, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class StatOrm:

    def __init__(self):
        super(StatOrm, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.group_name = ""  # 分组名称
        self.group_sub_name = ""  # 分组子名称
        self.key_name = ""  # key名称
        self.key_value = ""  # key值
        self.value_type = 0 # 输出类型(1-int，2-decimal)
        self.repeat_type = 0  # 去重方式(0不去重1当日去重2全部去重)
        self.sort_index = 0  # 排序号
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.is_show = 0  # 是否显示(1是0否)
        self.i1 = 0  # i1
        self.i2 = 0  # i2
        self.s1 = ""  # s1
        self.s2 = ""  # s2

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'module_id', 'group_name', 'group_sub_name', 'key_name', 'key_value', 'value_type', 'repeat_type', 'sort_index', 'create_date', 'is_show', 'i1', 'i2', 's1', 's2']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "stat_orm_tb"
