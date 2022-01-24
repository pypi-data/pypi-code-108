# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:55:09
@LastEditTime: 2021-07-29 18:30:54
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class FriendLinkModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(FriendLinkModel, self).__init__(FriendLink, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class FriendLink:

    def __init__(self):
        super(FriendLink, self).__init__()
        self.id = 0  # id
        self.title = ""  # 标题
        self.product_id = 0  # 产品id（0-其他，-1未选择）
        self.ad_pic = ""  # 互推广告图
        self.big_pic = ""  # 互推大图
        self.product_link = ""  # 产品链接地址
        self.associated_url = ""  # 关联地址
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'title', 'product_id', 'ad_pic', 'big_pic', 'product_link', 'associated_url', 'sort_index', 'is_release', 'release_date', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "friend_link_tb"
