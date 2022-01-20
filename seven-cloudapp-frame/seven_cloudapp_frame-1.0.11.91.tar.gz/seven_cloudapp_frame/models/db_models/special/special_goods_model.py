# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-28 16:41:14
@LastEditTime: 2021-08-10 18:06:59
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class SpecialGoodsModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(SpecialGoodsModel, self).__init__(SpecialGoods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class SpecialGoods:

    def __init__(self):
        super(SpecialGoods, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用唯一标识
        self.goods_id = ""  # 商品ID
        self.goods_name = ""  # 商品名称
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'goods_id', 'goods_name', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "special_goods_tb"
