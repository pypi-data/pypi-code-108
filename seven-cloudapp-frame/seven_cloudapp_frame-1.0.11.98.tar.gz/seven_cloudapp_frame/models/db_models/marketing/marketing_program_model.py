# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-03 15:45:17
@LastEditTime: 2021-08-03 15:45:58
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class MarketingProgramModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(MarketingProgramModel, self).__init__(MarketingProgram, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class MarketingProgram:

    def __init__(self):
        super(MarketingProgram, self).__init__()
        self.id = 0  # id
        self.link_title = ""  # 链接标题
        self.link_url = ""  # 链接地址
        self.content = ""  # 内容说明
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'link_title', 'link_url', 'content', 'sort_index', 'is_release', 'release_date', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "marketing_program_tb"
