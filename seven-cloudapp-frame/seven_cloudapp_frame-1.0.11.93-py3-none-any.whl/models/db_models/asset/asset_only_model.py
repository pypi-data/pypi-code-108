# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-15 17:17:08
@LastEditTime: 2021-09-02 20:41:40
@LastEditors: HuangJianYi
@Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *

class AssetOnlyModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(AssetOnlyModel, self).__init__(AssetOnly, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class AssetOnly:

    def __init__(self):
        super(AssetOnly, self).__init__()
        self.id = 0  # id
        self.id_md5 = 0  # id_md5(act_id+user_id+only_id)md5int生成
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动ID
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.only_id = ""  # 唯一标识(用于并发操作时校验避免重复操作)
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'id_md5', 'app_id', 'act_id', 'user_id', 'open_id', 'only_id', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "asset_only_tb"
