# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-10 10:09:06
@LastEditTime: 2021-09-02 17:41:04
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class TaskCountModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(TaskCountModel, self).__init__(TaskCount, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class TaskCount:

    def __init__(self):
        super(TaskCount, self).__init__()
        self.id = 0  # 标识
        self.id_md5 = 0  # id_md5(actid+moduleid+tasktype+tasksubtype+userid)md5int生成
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.task_type = 0  # 任务类型（枚举TaskType）
        self.task_sub_type = ""  # 任务子类型(用于指定任务里的再细分，比如:指定金额任务分不同档位金额)
        self.complete_count = 0  # 任务完成数
        self.now_count = 0  # 当前计数
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.modify_day = 0  # 更新天(19000101)
        self.remark = ""  # 备注

    @classmethod
    def get_field_list(self):
        return ['id', 'id_md5', 'app_id', 'act_id', 'module_id', 'user_id', 'open_id', 'task_type', 'task_sub_type', 'complete_count', 'now_count', 'create_date', 'modify_date', 'modify_day', 'remark']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "task_count_tb"
