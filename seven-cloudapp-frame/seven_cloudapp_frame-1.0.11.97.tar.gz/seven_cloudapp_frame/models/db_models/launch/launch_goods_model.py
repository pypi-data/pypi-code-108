# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:55:09
@LastEditTime: 2021-08-10 18:06:23
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class LaunchGoodsModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(LaunchGoodsModel, self).__init__(LaunchGoods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class LaunchGoods:

    def __init__(self):
        super(LaunchGoods, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用唯一标识
        self.act_id = 0  # 活动标识
        self.goods_id = ""  # 商品ID
        self.is_launch = 0  # 是否投放(0：不投放 1：投放)
        self.is_sync = 0  # 是否同步（0不同步 1：同步）
        self.error_message = ""  # 同步失败原因
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.launch_date = "1900-01-01 00:00:00"  # 投放时间
        self.sync_date = "1900-01-01 00:00:00"  # 同步时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'goods_id', 'is_launch', 'is_sync', 'error_message', 'create_date', 'launch_date', 'sync_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "launch_goods_tb"
