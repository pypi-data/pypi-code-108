# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 15:41:57
@LastEditTime: 2021-11-25 10:31:12
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class ThemeInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ThemeInfoModel, self).__init__(ThemeInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ThemeInfo:

    def __init__(self):
        super(ThemeInfo, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用唯一标识
        self.theme_name = ""  # 主题名称
        self.server_json = ""  # 服务端内容json
        self.out_id = ""  # 外部id
        self.style_type = 0  # 样式类型
        self.sort_index = 0  # 排序号
        self.is_release = 0  # 是否发布（1发布0未发布）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'theme_name', 'server_json', 'out_id', 'style_type', 'sort_index', 'is_release', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "theme_info_tb"
