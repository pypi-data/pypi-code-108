# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:57:24
@LastEditTime: 2021-09-02 15:31:21
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class TaoPayOrderModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(TaoPayOrderModel, self).__init__(TaoPayOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class TaoPayOrder:

    def __init__(self):
        super(TaoPayOrder, self).__init__()
        self.id = 0  # id(act_id+user_id+guid)md5int生成
        self.ascription_type = 0  # 归属类型（0-抽奖次数订单1-邮费次数订单2-任务订单）
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.goods_code = ""  # 商品编码
        self.goods_name = ""  # 商品名称
        self.sku_id = ""  # sku_id
        self.sku_name = ""  # sku_name
        self.buy_num = 0  # 购买数量
        self.pay_price = 0  # 购买金额
        self.main_pay_order_no = ""  # 淘宝主订单号
        self.sub_pay_order_no = ""  # 淘宝子订单号
        self.order_status = ""  # 订单状态
        self.asset_type = 0  # 资产类型(1-次数2-积分3-价格档位)
        self.asset_object_id = ""  # 资产对象标识
        self.surplus_count = 0  # 剩余资产值
        self.prize_ids = ""  # 奖品ID列表（逗号隔开）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.pay_date = "1900-01-01 00:00:00"  # 支付时间
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
        return ['id', 'ascription_type', 'app_id', 'act_id', 'user_id', 'open_id', 'user_nick', 'goods_code', 'goods_name', 'sku_id', 'sku_name', 'buy_num', 'pay_price', 'main_pay_order_no', 'sub_pay_order_no', 'order_status', 'asset_type', 'asset_object_id', 'surplus_count', 'prize_ids', 'create_date', 'pay_date', 'i1', 'i2', 'i3', 'i4', 'i5', 's1', 's2', 's3', 's4', 's5', 'd1', 'd2']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "tao_pay_order_tb"
