# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-11-25 18:38:13
@LastEditTime: 2021-12-29 14:54:12
@LastEditors: HuangJianYi
@Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class CmsPlaceModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(CmsPlaceModel, self).__init__(CmsPlace, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class CmsPlace:

    def __init__(self):
        super(CmsPlace, self).__init__()
        self.id = 0  # id
        self.place_name = ""  # 位置名称
        self.place_type = 1  # 位置类型(1商家后台2中台)
        self.config_json = ""  # 自定义配置json
        self.field_config_json = ""  # 字段配置json
        self.remark = ""  # 备注
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'place_type', 'place_name', 'config_json', 'field_config_json', 'remark', 'is_release', 'release_date', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "cms_place_tb"
