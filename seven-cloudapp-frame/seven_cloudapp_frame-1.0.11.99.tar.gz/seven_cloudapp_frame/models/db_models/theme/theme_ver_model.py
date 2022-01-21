# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 15:41:57
@LastEditTime: 2021-07-29 18:38:20
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class ThemeVerModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ThemeVerModel, self).__init__(ThemeVer, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ThemeVer:

    def __init__(self):
        super(ThemeVer, self).__init__()
        self.id = 0  # id
        self.theme_id = 0  # 主题标识
        self.out_id = ""  # 外部id
        self.client_json = ""  # 客户端内容json
        self.ver_no = ""  # 客户端版本号
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'theme_id', 'out_id', 'client_json', 'ver_no', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "theme_ver_tb"
