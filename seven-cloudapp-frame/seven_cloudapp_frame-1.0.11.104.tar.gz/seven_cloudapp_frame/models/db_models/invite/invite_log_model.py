# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-12 17:38:51
@LastEditTime: 2021-11-24 10:38:24
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class InviteLogModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(InviteLogModel, self).__init__(InviteLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class InviteLog:

    def __init__(self):
        super(InviteLog, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 邀请人用户标识
        self.open_id = ""  # 邀请人OpenID
        self.invite_user_id = "" # 受邀人用户标识
        self.invite_open_id = ""  # 受邀人OpenID
        self.invite_user_nick = ""  # 受邀人昵称
        self.invite_avatar = ""  # 受邀人头像
        self.is_handle = 0  # 是否处理（1处理0未处理）
        self.is_invited_handle = 0  #受邀人是否处理（1处理0未处理）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.create_day = 0  # 创建天

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'user_id', 'open_id', 'invite_user_id', 'invite_open_id', 'invite_user_nick', 'invite_avatar', 'is_handle', 'is_invited_handle', 'create_date', 'create_day']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "invite_log_tb"
