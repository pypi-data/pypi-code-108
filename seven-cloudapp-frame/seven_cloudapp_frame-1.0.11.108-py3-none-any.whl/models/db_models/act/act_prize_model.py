# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:59:46
@LastEditTime: 2021-11-29 14:10:53
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class ActPrizeModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActPrizeModel, self).__init__(ActPrize, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ActPrize:

    def __init__(self):
        super(ActPrize, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.ascription_type = 0  # 奖品归属类型（0-活动奖品1-任务奖品2-兑换奖品）业务自定义从101开始
        self.prize_name = ""  # 奖品名称
        self.prize_title = ""  # 奖品子标题
        self.prize_pic = ""  # 奖品图
        self.prize_detail_json = ""  # 奖品详情json
        self.goods_id = ""  # 商品ID
        self.goods_code = ""  # 商品编码
        self.goods_code_list = ""  # 多个sku商品编码
        self.goods_type = 0  # 物品类型（1虚拟2实物）
        self.prize_type = 0  # 奖品类型(1现货2优惠券3红包4参与奖5预售)
        self.prize_price = 0  # 奖品价格
        self.probability = 0  # 奖品权重
        self.chance = 0  # 概率
        self.prize_limit = 0  # 中奖限制
        self.is_prize_notice = 0  # 是否显示跑马灯(1是0否)
        self.surplus = 0  # 奖品库存
        self.is_surplus = 0  # 是否显示奖品库存（1显示0-不显示）
        self.prize_total = 0  # 奖品总数
        self.hand_out = 0  # 已发出数量
        self.lottery_type = 0  # 出奖类型（1概率出奖 2强制概率）
        self.tag_name = ""  # 标签名称(奖项名称)
        self.tag_id = 0  # 标签ID(奖项标识)
        self.sort_index = 0  # 排序
        self.is_del = 0  # 是否删除（1是0否）
        self.is_release = 0  # 是否发布（1是0否）
        self.is_sku = 0  # 是否有SKU
        self.sku_json = ""  # sku详情json
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
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
        return ['id', 'app_id', 'act_id', 'module_id', 'ascription_type', 'prize_name', 'prize_title', 'prize_pic', 'prize_detail_json', 'goods_id', 'goods_code', 'goods_code_list', 'goods_type', 'prize_type', 'prize_price', 'probability', 'chance', 'prize_limit', 'is_prize_notice', 'surplus', 'is_surplus', 'prize_total', 'hand_out', 'lottery_type', 'tag_name', 'tag_id', 'sort_index', 'is_del', 'is_release', 'is_sku', 'sku_json', 'create_date', 'modify_date', 'i1', 'i2', 'i3', 'i4', 'i5', 's1','s2', 's3', 's4', 's5', 'd1', 'd2']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_prize_tb"
