# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:55:09
@LastEditTime: 2021-12-01 17:34:14
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class PrizeOrderModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PrizeOrderModel, self).__init__(PrizeOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class PrizeOrder:

    def __init__(self):
        super(PrizeOrder, self).__init__()
        self.id = 0  # id
        self.order_no = ""  # 订单号
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.real_name = ""  # 真实姓名
        self.telephone = ""  # 手机号码
        self.province = ""  # 所在省
        self.city = ""  # 所在市
        self.county = ""  # 所在区
        self.street = ""  # 所在街道
        self.address = ""  # 收货地址
        self.deliver_date = "1900-01-01 00:00:00"  # 发货时间
        self.express_no = ""  # 快递单号
        self.express_company = ""  # 快递公司
        self.order_status = 0  # 订单状态（-1未付款-2付款中0未发货1已发货2不予发货3已退款4交易成功）
        self.buyer_remark = ""  # 买家备注
        self.seller_remark = ""  # 卖家备注
        self.order_price = 0  # 订单金额
        self.is_free_freight = 0  # 是否包邮
        self.freight_price = 0  # 运费金额
        self.freight_pay_order_no = ""  # 运费支付单号
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.create_month = 0  # 创建月
        self.create_day = 0  # 创建天
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间
        self.sync_status = 0  # 订单同步状态，用于遁甲或者ERP同步订单（0未同步，1同步成功，2同步失败）
        self.sync_date = "1900-01-01 00:00:00"  # 同步时间
        self.sync_count = 0  # 同步次数
        self.sync_result = ""  # 同步结果
        self.i1 = 0  # i1
        self.i2 = 0  # i2
        self.i3 = 0  # i3
        self.i4 = 0  # i4
        self.i5 = 0  # i5
        self.s1 = ""  # s1
        self.s2 = ""  # s2
        self.s3 = ""  # s3
        self.s4 = ""  # s4
        self.s5 = ""  # s5
        self.d1 = "1900-01-01 00:00:00"  # d1
        self.d2 = "1900-01-01 00:00:00"  # d2

    @classmethod
    def get_field_list(self):
        return ['id', 'order_no', 'app_id', 'act_id', 'module_id', 'user_id', 'open_id', 'user_nick', 'real_name', 'telephone', 'province', 'city', 'county', 'street', 'address', 'deliver_date', 'express_no', 'express_company', 'order_status', 'buyer_remark', 'seller_remark', 'order_price', 'is_free_freight', 'freight_price', 'freight_pay_order_no', 'create_date', 'create_month', 'create_day', 'modify_date', 'sync_status', 'sync_date', 'sync_count', 'sync_result', 'i1', 'i2', 'i3', 'i4', 'i5', 's1','s2', 's3', 's4', 's5', 'd1', 'd2']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "prize_order_tb"
