# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-19 22:41:48
@LastEditTime: 2021-09-02 18:30:45
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class AssetInventoryModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(AssetInventoryModel, self).__init__(AssetInventory, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class AssetInventory:

    def __init__(self):
        super(AssetInventory, self).__init__()
        self.id = 0  # id
        self.id_md5 = 0  # id_md5(act_id+user_id+asset_type+asset_object_id+create_day)md5int生成
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.asset_type = 0  # 资产类型(1-次数2-积分3-价格档位)
        self.asset_object_id = ""  # 对象标识
        self.inc_value = 0  # 增加值
        self.dec_value = 0  # 消耗值
        self.history_value = 0  # 今天之前的资产值
        self.now_value = 0  # 当前的资产值
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.create_day = 0  # 创建时间天
        self.process_count = 0  # 处理次数
        self.process_date = "1900-01-01 00:00:00"  # 处理时间

    @classmethod
    def get_field_list(self):
        return ['id', 'id_md5', 'app_id', 'act_id', 'user_id', 'open_id', 'user_nick', 'asset_type', 'asset_object_id', 'inc_value', 'dec_value', 'history_value', 'now_value', 'create_date', 'create_day', 'process_count', 'process_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "asset_inventory_tb"
