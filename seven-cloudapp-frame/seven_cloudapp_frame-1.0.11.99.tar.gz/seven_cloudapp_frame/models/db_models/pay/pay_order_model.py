# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-16 19:14:40
@LastEditTime: 2021-09-28 18:39:01
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class PayOrderModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PayOrderModel, self).__init__(PayOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class PayOrder:

    def __init__(self):
        super(PayOrder, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.pay_order_no = ""  # 支付单号
        self.order_name = ""  # 订单名称
        self.order_desc = ""  # 订单描述
        self.source_type = 0  # 来源类型（1-购买2-邮费.业务自定义类型从101起，避免跟公共冲突）
        self.out_order_no = ""  # 平台交易单号
        self.order_status = 0  # 订单状态:0等待买家付款1付款成功2支付关闭11交易成功20退款关闭
        self.pay_amount = 0  # 支付金额（单位：元）
        self.refund_amount = 0  # 退款金额（单位：元）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.pay_date = "1900-01-01 00:00:00"  # 支付时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'user_id', 'open_id', 'pay_order_no', 'order_name', 'order_desc', 'source_type', 'out_order_no', 'order_status', 'pay_amount', 'refund_amount', 'create_date', 'pay_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "pay_order_tb"
