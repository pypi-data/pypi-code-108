# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-15 15:05:22
@LastEditTime: 2021-07-29 18:33:10
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class MiddlerProductModel(CacheModel):
    def __init__(self, db_connect_key='db_middler_platform', sub_table=None, db_transaction=None, context=None):
        super(MiddlerProductModel, self).__init__(MiddlerProduct, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class MiddlerProduct:

    def __init__(self):
        super(MiddlerProduct, self).__init__()
        self.id = 0  # id
        self.guid = ""  # guid
        self.app_key = 0  # app_key
        self.app_secret = ""  # app_secret
        self.product_name = ""  # 产品名称
        self.product_type = 0  # 产品类型：1云开发，2云应用
        self.product_icon = ""  # 产品图标
        self.db_key = ""  # 数据库key
        self.contains_name = ""  # 产品服务名称列表（如：一起来盖楼,互动游戏宝,互动PK宝盒）
        self.is_release = 0  # 是否发布（1是0否）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'guid', 'app_key', 'app_secret', 'product_name', 'product_type', 'product_icon', 'db_key', 'contains_name', 'is_release', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "middler_product_tb"
