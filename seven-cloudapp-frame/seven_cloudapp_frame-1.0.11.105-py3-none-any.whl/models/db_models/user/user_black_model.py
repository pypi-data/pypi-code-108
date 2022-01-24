# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-22 16:03:01
@LastEditTime: 2021-07-29 18:39:05
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class UserBlackModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(UserBlackModel, self).__init__(UserBlack, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class UserBlack:

    def __init__(self):
        super(UserBlack, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.black_type = 0  # 拉黑类型（1自动2手动）
        self.reason = ""  # 申请原因
        self.audit_status = 0  # 审核状态(0黑名单1申请中2同意3拒绝)
        self.audit_remark = ""  # 审核备注
        self.refund_count = 0  # 退款次数
        self.refund_order_data = ""  # 退款主订单号(逗号分隔)
        self.create_date = "1900-01-01 00:00:00"  # 申请时间
        self.audit_date = "1900-01-01 00:00:00"  # 审核时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'user_id', 'open_id', 'user_nick', 'black_type', 'reason', 'audit_status', 'audit_remark', 'refund_count', 'refund_order_data', 'create_date', 'audit_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "user_black_tb"
