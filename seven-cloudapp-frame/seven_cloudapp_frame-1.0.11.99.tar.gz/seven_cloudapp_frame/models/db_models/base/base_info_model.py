# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-20 10:09:52
@LastEditTime: 2021-07-29 18:30:00
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class BaseInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(BaseInfoModel, self).__init__(BaseInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class BaseInfo:

    def __init__(self):
        super(BaseInfo, self).__init__()
        self.id = 0  # id
        self.guid = ""  # guid
        self.product_name = ""  # 产品名称
        self.product_icon = ""  # 产品图标
        self.product_desc = ""  # 产品简介
        self.service_market_url = ""  # 服务市场链接
        self.customer_service = ""  # 客服号
        self.experience_pic = ""  # 案例二维码图
        self.client_ver = ""  # 客户端版本号
        self.server_ver = ""  # 服务端版本号
        self.update_function = ""  # 版本更新内容
        self.update_function_b = ""  # 千牛端版本更新内容
        self.store_study_url = ""  # 店铺装修教程图文地址（如何上架小程序）
        self.study_url = ""  # 后台配置图文教程
        self.video_url = ""  # 后台配置视频教程
        self.course_url = ""  # 主账号授权子账号教程
        self.decoration_poster_json = ""  # 装修海报
        self.menu_config_json = ""  # 菜单配置信息
        self.is_remind_phone = 0  # 是否提醒提示配置手机号
        self.is_force_update = 0  # 是个强制更新客户端版本
        self.is_contact_us = 0  # 是否提醒联系我们
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间
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
        return ['id', 'guid', 'product_name', 'product_icon', 'product_desc', 'service_market_url', 'customer_service', 'experience_pic', 'client_ver', 'server_ver', 'update_function', 'update_function_b', 'store_study_url', 'study_url', 'video_url', 'course_url', 'decoration_poster_json', 'menu_config_json', 'is_remind_phone', 'is_force_update', 'is_contact_us', 'create_date', 'modify_date', 'i1', 'i2', 'i3', 'i4', 's1', 's2', 's3', 's4']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "base_info_tb"
