# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:55:09
@LastEditTime: 2021-12-17 10:50:25
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class IpInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(IpInfoModel, self).__init__(IpInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class IpInfo:

    def __init__(self):
        super(IpInfo, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.ip_name = ""  # ip名称
        self.ip_type = 0  # ip类型
        self.ip_pic = ""  # ip图片
        self.show_pic = ""  # 展示图片
        self.ip_summary = ""  # ip描述
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1发布0未发布）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'ip_name', 'ip_type', 'ip_pic', 'show_pic', 'ip_summary', 'sort_index', 'is_release', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "ip_info_tb"
