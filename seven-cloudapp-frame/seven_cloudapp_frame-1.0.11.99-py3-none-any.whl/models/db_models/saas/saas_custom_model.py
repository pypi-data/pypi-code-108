# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 17:00:16
@LastEditTime: 2021-07-29 18:34:56
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class SaasCustomModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(SaasCustomModel, self).__init__(SaasCustom, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class SaasCustom:

    def __init__(self):
        super(SaasCustom, self).__init__()
        self.id = 0  #
        self.cloud_app_id = 0  # 云应用id
        self.store_user_nick = ""  # 店铺主帐号名称（会员名）
        self.app_name = ""  # 应用名称
        self.app_icon = ""  # 应用图标
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.service_date_start = "1900-01-01 00:00:00"  # 服务开始时间
        self.service_date_end = "1900-01-01 00:00:00"  # 服务结束时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'cloud_app_id', 'store_user_nick', 'app_name', 'app_icon', 'is_release', 'release_date', 'service_date_start', 'service_date_end', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "saas_custom_tb"
