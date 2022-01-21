# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:55:09
@LastEditTime: 2021-08-04 10:56:42
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class ActModuleModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActModuleModel, self).__init__(ActModule, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ActModule:

    def __init__(self):
        super(ActModule, self).__init__()
        self.id = 0  #
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_name = ""  # 模块名称
        self.module_sub_name = ""  # 模块短名称
        self.start_date = "1900-01-01 00:00:00"  # 开始时间
        self.end_date = "1900-01-01 00:00:00"  # 结束时间
        self.skin_id = 0  # 皮肤标识
        self.module_pic = ""  # 模块图片
        self.module_desc = ""  # 描述信息
        self.price = 0  # 价格
        self.price_gear_id = 0  # 档位标识
        self.ip_id = 0  # IP标识
        self.join_ways = 0  # 活动参与条件（0所有1关注店铺2加入会员3指定用户）
        self.is_fictitious = 0  # 是否开启虚拟中奖（1是0否）
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.is_del = 0  # 是否删除（1是0否）
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
        return ['id', 'app_id', 'act_id', 'module_name', 'module_sub_name', 'start_date', 'end_date', 'skin_id', 'module_pic', 'module_desc', 'price', 'price_gear_id', 'ip_id', 'join_ways', 'is_fictitious', 'sort_index', 'is_release', 'release_date', 'create_date', 'modify_date', 'is_del', 'i1', 'i2', 'i3', 'i4', 'i5', 's1', 's2', 's3', 's4', 's5', 'd1', 'd2']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_module_tb"
