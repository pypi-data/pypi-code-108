# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-20 10:09:52
@LastEditTime: 2021-07-29 18:28:39
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class AppInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(AppInfoModel, self).__init__(AppInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class AppInfo:

    def __init__(self):
        super(AppInfo, self).__init__()
        self.id = 0  # id
        self.store_name = ""  # 店铺名称
        self.store_user_nick = ""  # 店铺主帐号名称（会员名）
        self.store_id = 0  # 店铺ID
        self.store_icon = ""  # 店铺图标
        self.seller_id = ""  # 卖家ID
        self.app_id = ""  # app_id
        self.app_name = ""  # 应用名称
        self.app_icon = ""  # 应用图标
        self.app_url = ""  # 小程序链接
        self.app_ver = ""  # 应用版本
        self.app_key = ""  # 应用密钥
        self.access_token = ""  # access_token
        self.preview_url = ""  # 预览地址
        self.app_desc = ""  # 应用介绍
        self.template_id = ""  # 模板标识
        self.template_ver = ""  # 模板版本号
        self.clients = ""  # 适用客户端（taobao和tmall）
        self.app_telephone = ""  # 手机号码
        self.is_instance = 0  # 是否实例化：0-未实例化，1-已实例化
        self.instance_date = "1900-01-01 00:00:00"  # 实例化时间
        self.is_setting = 0  # 是否完成数据配置：0-未完成，1-已配置
        self.expiration_date = "1900-01-01 00:00:00"  # 过期时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.current_limit_count = 0  # 限流数量
        self.i1 = 0  # i1
        self.i2 = 0  # i2
        self.i3 = 0  # i3
        self.i4 = 0  # i4
        self.s1 = ""  # s1
        self.s2 = ""  # s2
        self.s3 = ""  # s3
        self.s4 = ""  # s4

    @classmethod
    def get_field_list(self):
        return ['id', 'store_name', 'store_user_nick', 'store_id', 'store_icon', 'seller_id', 'app_id', 'app_name', 'app_icon', 'app_url', 'app_ver', 'app_key', 'access_token', 'preview_url', 'app_desc', 'template_id', 'template_ver', 'clients', 'app_telephone', 'is_instance', 'instance_date', 'is_setting', 'expiration_date', 'modify_date', 'current_limit_count', 'i1', 'i2', 'i3', 'i4', 's1', 's2', 's3', 's4']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "app_info_tb"
