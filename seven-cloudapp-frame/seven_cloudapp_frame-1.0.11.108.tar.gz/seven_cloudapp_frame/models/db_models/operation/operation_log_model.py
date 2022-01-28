# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 10:11:35
@LastEditTime: 2021-08-02 14:39:04
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class OperationLogModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(OperationLogModel, self).__init__(OperationLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class OperationLog:

    def __init__(self):
        super(OperationLog, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.operation_type = 0  # 操作类型：1-add，2-update，3-delete
        self.title = ""  # 标题
        self.detail = ""  # 当前信息
        self.update_detail = ""  # 更新之后的信息
        self.request_params = ""  # 传入的参数
        self.model_name = ""  # 模块或表名称
        self.protocol = ""  # protocol(http或https)
        self.method = ""  # method
        self.handler_name = ""  # handler_name
        self.request_host = ""  # request_host
        self.request_uri = ""  # request_uri
        self.remote_ip = ""  # remote_ip
        self.operate_user_id = ""  # 操作人标识
        self.operate_user_name = ""  # 操作人名称
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'operation_type', 'title', 'detail', 'update_detail', 'request_params', 'model_name', 'protocol', 'method', 'handler_name', 'request_host', 'request_uri', 'remote_ip', 'operate_user_id', 'operate_user_name', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "operation_log_tb"
