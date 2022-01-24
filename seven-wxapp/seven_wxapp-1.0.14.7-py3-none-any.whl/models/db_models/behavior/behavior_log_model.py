# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-04-09 09:23:02
@LastEditTime: 2021-04-21 14:41:57
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class BehaviorLogModel(BaseModel):
    def __init__(self, db_connect_key='db_wxapp', sub_table=None, db_transaction=None):
        super(BehaviorLogModel, self).__init__(BehaviorLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类

class BehaviorLog:

    def __init__(self):
        super(BehaviorLog, self).__init__()
        self.id = 0  # id
        self.act_id = 0  # act_id
        self.user_id = 0  # user_id
        self.orm_id = 0  # 统计映射表id
        self.inc_value = 0  # 增加的值
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.create_day = 0  # 创建天

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'user_id', 'orm_id', 'inc_value', 'create_date', 'create_day']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "behavior_log_tb"
