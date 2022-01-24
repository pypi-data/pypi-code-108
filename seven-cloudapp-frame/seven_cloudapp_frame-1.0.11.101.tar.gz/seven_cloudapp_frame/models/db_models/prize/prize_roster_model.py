# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:55:09
@LastEditTime: 2021-11-29 14:10:17
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class PrizeRosterModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PrizeRosterModel, self).__init__(PrizeRoster, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class PrizeRoster:

    def __init__(self):
        super(PrizeRoster, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.order_no = ""  # 订单号
        self.source_type = 0  # 来源类型（0-活动奖品1-任务奖品2-兑换奖品）业务自定义从101开始
        self.source_object_id = ""  # 来源对象标识
        self.module_id = 0  # 活动模块标识
        self.module_name = ""  # 活动模块名称
        self.goods_type = 0  # 物品类型（1虚拟2实物）
        self.prize_type = 0  # 奖品类型(1现货2优惠券3红包4参与奖5预售)
        self.prize_id = 0  # 奖品标识
        self.prize_name = ""  # 奖品名称
        self.prize_pic = ""  # 奖品图
        self.prize_detail_json = ""  # 奖品详情json
        self.prize_price = 0  # 奖品价格
        self.tag_name = ""  # 标签名称(奖项名称)
        self.tag_id = 0  # 标签ID(奖项标识)
        self.logistics_status = 0  # 物流状态（0未发货1已发货2不予发货）
        self.prize_status = 0  # 奖品状态（0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货）
        self.pay_status = 0  # 支付状态(0未支付1已支付2已退款3处理中)
        self.goods_id = ""  # 商品ID
        self.goods_code = ""  # 商品编码
        self.goods_code_list = ""  # 多个sku商品编码
        self.is_sku = 0  # 是否有SKU
        self.sku_id = ""  # sku_id
        self.sku_name = ""  # sku_name
        self.sku_json = ""  # sku详情json
        self.main_pay_order_no = ""  # 支付主订单号
        self.sub_pay_order_no = ""  # 支付子订单号
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.request_code = ""  # 请求代码
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
        return [
            'id', 'app_id', 'act_id', 'user_id', 'open_id', 'user_nick', 'order_no', 'source_type', 'source_object_id', 'module_id', 'module_name', 'goods_type', 'prize_type', 'prize_id', 'prize_name', 'prize_pic', 'prize_detail_json', 'prize_price', 'tag_name', 'tag_id', 'logistics_status', 'prize_status', 'pay_status', 'goods_id', 'goods_code', 'goods_code_list', 'is_sku', 'sku_id', 'sku_name', 'sku_json', 'main_pay_order_no', 'sub_pay_order_no', 'create_date', 'request_code', 'i1', 'i2',
            'i3', 'i4', 'i5', 's1', 's2', 's3', 's4', 's5', 'd1', 'd2'
        ]

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "prize_roster_tb"
