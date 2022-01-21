# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-13 16:26:10
@LastEditTime: 2021-09-30 10:19:50
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class RefundOrderModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(RefundOrderModel, self).__init__(RefundOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class RefundOrder:

    def __init__(self):
        super(RefundOrder, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.pay_order_no = ""  # 支付单号
        self.refund_no = ""  # 退款单号
        self.out_refund_no = ""  # 平台退款单号
        self.out_order_no = ""  # 平台交易单号
        self.refund_amount = 0  # 退款金额
        self.refund_status = 0  # 退款状态 1商户申请退款中2退款处理中3退款成功4退款失败5退款关闭
        self.refund_reason = ""  # 退款理由
        self.refund_date = "1900-01-01 00:00:00"  # 退款时间
        self.refund_result_detail = ""  # 退款结果描述
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'user_id', 'open_id', 'pay_order_no', 'refund_no', 'out_refund_no', 'out_order_no', 'refund_amount', 'refund_status', 'refund_reason', 'refund_date', 'refund_result_detail', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "refund_order_tb"
