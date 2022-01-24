# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:58:31
@LastEditTime: 2021-12-14 15:43:26
@LastEditors: HuangJianYi
@Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *

class ActInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActInfoModel, self).__init__(ActInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ActInfo:

    def __init__(self):
        super(ActInfo, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_name = ""  # 活动名称
        self.act_type = 0  # 活动类型
        self.theme_id = 0  # 主题标识
        self.is_visit_store = 0  # 是否开启访问店铺
        self.store_url = ""  # 店铺地址
        self.close_word = ""  # 关闭小程序文案
        self.is_share = 0  # 是否开启分享(1是0否)
        self.share_desc_json = ""  # 分享内容
        self.is_rule = 0  # 是否显示规则（1是0否）
        self.rule_desc_json = ""  # 规则内容
        self.start_date = "1900-01-01 00:00:00"  # 开始时间
        self.end_date = "1900-01-01 00:00:00"  # 结束时间
        self.is_black = 0  # 是否开启黑名单
        self.refund_count = 0  # 退款次数
        self.finish_menu_config_json = ""  # 已配置的菜单json
        self.is_finish = 0  # 是否完成配置
        self.is_launch = 0  # 是否开启投放（1是0否）
        self.is_del = 0  # 是否删除（1是0否）
        self.join_ways = 0  # 活动参与条件（0所有1关注店铺2加入会员3指定用户）
        self.is_fictitious = 0  # 是否开启虚拟中奖（1是0否）
        self.task_asset_type_json = ""  # 任务货币类型（字典数组）
        self.lc_order_id = ""  # 小部件orderId
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.sort_index = 0  # 排序号
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
        return ['id', 'app_id', 'act_name', 'act_type', 'theme_id', 'is_visit_store', 'store_url', 'close_word', 'is_share', 'share_desc_json', 'is_rule', 'rule_desc_json', 'start_date', 'end_date', 'is_black', 'refund_count', 'finish_menu_config_json', 'is_finish', 'is_launch', 'is_del', 'join_ways', 'is_fictitious', 'task_asset_type_json', 'lc_order_id', 'is_release', 'release_date', 'sort_index', 'create_date', 'modify_date', 'i1', 'i2', 'i3', 'i4', 'i5', 's1', 's2', 's3', 's4', 's5', 'd1', 'd2']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_info_tb"
