# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 15:41:57
@LastEditTime: 2022-01-20 11:32:37
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class SkinInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(SkinInfoModel, self).__init__(SkinInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class SkinInfo:

    def __init__(self):
        super(SkinInfo, self).__init__()
        self.id = 0  # id
        self.skin_name = ""  # 皮肤名称
        self.theme_id = 0  # 主题标识
        self.style_type = 0  # 样式类型
        self.client_json = ""  # 客户端内容json
        self.server_json = ""  # 服务端内容json
        self.out_id = ""  # 外部id
        self.theme_out_id = ""  # 外部主题id
        self.sort_index = 0  # 排序
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'skin_name', 'theme_id', 'style_type', 'client_json', 'server_json', 'out_id', 'theme_out_id', 'sort_index', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "skin_info_tb"
