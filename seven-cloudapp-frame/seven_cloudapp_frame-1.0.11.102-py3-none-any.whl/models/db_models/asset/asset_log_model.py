# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-15 17:17:08
@LastEditTime: 2021-10-11 16:24:40
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class AssetLogModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(AssetLogModel, self).__init__(AssetLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class AssetLog:

    def __init__(self):
        super(AssetLog, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.user_nick = ""  # 昵称
        self.log_title = ""  # 标题
        self.info_json = ""  # 详情信息
        self.asset_type = 0  # 资产类型(1-次数2-积分3-价格档位)
        self.asset_object_id = ""  # 资产对象标识（比如资产类型是价格档位则对应档位id）
        self.source_type = 0  # 来源类型（1-购买2-任务3-手动配置4-抽奖5-回购.业务自定义类型从101起，避免跟公共冲突）
        self.source_object_id = ""  # 来源对象标识(比如来源类型是任务则对应任务类型)
        self.source_object_name = ""  # 来源对象名称(比如来源类型是任务则对应任务名称)
        self.only_id = ""  # 唯一标识(用于并发操作时校验避免重复操作)
        self.operate_type = 0  # 操作类型 （0累计 1消耗）
        self.operate_value = 0  # 操作值
        self.history_value = 0  # 历史值
        self.now_value = 0  # 当前值
        self.handler_name = ""  # 接口名称
        self.request_code = ""  # 请求代码
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.create_day = 0  # 创建天
        self.warn_date = "1900-01-01 00:00:00"  # 预警时间
        self.warn_day = 0  # 预警天
        self.i1 = 0  # i1
        self.s1 = ""  # s1

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'module_id', 'user_id', 'open_id', 'user_nick', 'log_title', 'info_json', 'asset_type', 'asset_object_id', 'source_type', 'source_object_id', 'source_object_name', 'only_id', 'operate_type', 'operate_value', 'history_value', 'now_value', 'handler_name', 'request_code', 'create_date', 'create_day', 'warn_date', 'warn_day', 'i1', 's1']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "asset_log_tb"
