# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:55:09
@LastEditTime: 2021-07-29 18:28:08
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class ActTypeModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActTypeModel, self).__init__(ActType, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ActType:

    def __init__(self):
        super(ActType, self).__init__()
        self.id = 0  # id
        self.type_name = ""  # 类型名称
        self.type_sub_name = ""  # 类型子名称
        self.type_pic = ""  # 类型图片
        self.market_ids = ""  # 所属营销方案id串（逗号分隔多个）
        self.experience_pic = ""  # 体验二维码图
        self.play_process_json = ""  # 玩法流程  举例:{"title": "玩法流程", "process_list": ["1.用户可通过付费购买获得拆盲盒次数"]}
        self.suit_behavior_json = ""  # 适用行为 举例:{"title": "适用行业", "behavior_list": ["所有行业"]}
        self.market_function_json = ""  # 营销功能 举例:{"title": "营销功能", "function_list": ["提升商品销量", "提升商品权重"]}
        self.type_desc = ""  # 类型描述
        self.task_asset_type_json = ""  # 任务货币类型（字典数组）
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'type_name', 'type_sub_name', 'type_pic', 'market_ids', 'experience_pic', 'play_process_json', 'suit_behavior_json', 'market_function_json', 'type_desc', 'task_asset_type_json', 'sort_index', 'is_release', 'release_date', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_type_tb"
