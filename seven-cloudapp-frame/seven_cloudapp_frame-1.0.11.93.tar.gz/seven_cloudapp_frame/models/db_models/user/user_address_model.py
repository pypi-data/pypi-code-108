# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-11-01 18:56:43
@LastEditTime: 2021-11-02 18:33:34
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class UserAddressModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(UserAddressModel, self).__init__(UserAddress, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class UserAddress:

    def __init__(self):
        super(UserAddress, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.real_name = ""  # 真实姓名
        self.telephone = ""  # 手机号码
        self.is_default = 0  # 是否默认地址（1是0否）
        self.province = ""  # 省
        self.city = ""  # 市
        self.county = ""  # 区
        self.street = ""  # 所在街道
        self.address = ""  # 收货地址
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'user_id', 'open_id', 'real_name', 'telephone', 'is_default', 'province', 'city', 'county', 'street', 'address', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "user_address_tb"
