# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:57:24
@LastEditTime: 2021-12-10 14:32:30
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class TaoCouponModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(TaoCouponModel, self).__init__(TaoCoupon, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class TaoCoupon:

    def __init__(self):
        super(TaoCoupon, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.prize_id = 0  # 奖品标识
        self.coupon_type = 0  # 优惠券类型(0无1店铺优惠券2商品优惠券3会员专享优惠券)
        self.coupon_url = ""  # 优惠劵地址
        self.coupon_price = 0  # 优惠券面额
        self.use_sill_price = 0  # 使用门槛金额
        self.right_ename = ""  # 发放的权益(奖品)唯一标识
        self.pool_id = ""  # 奖池ID
        self.coupon_start_date = "1900-01-01 00:00:00"  # 优惠券开始时间
        self.coupon_end_date = "1900-01-01 00:00:00"  # 优惠券结束时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'module_id', 'prize_id', 'coupon_type', 'coupon_url', 'coupon_price', 'use_sill_price', 'right_ename', 'pool_id', 'coupon_start_date', 'coupon_end_date', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "tao_coupon_tb"
