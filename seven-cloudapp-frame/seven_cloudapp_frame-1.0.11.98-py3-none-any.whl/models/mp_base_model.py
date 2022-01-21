# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-12-20 16:07:52
@LastEditTime: 2022-01-13 14:53:11
@LastEditors: HuangJianYi
@Description: 中台接口相关处理业务模型
"""
from seven_framework import *

from seven_cloudapp_frame.libs.customize.seven_helper import SevenHelper

class MPBaseModel():
    """
    :description: 中台接口相关处理业务模型
    """
    def __init__(self, context=None, logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def get_project_code_list(self, project_code):
        """
        :description:  获取公共功能列表
        :param project_code:收费项目代码（服务管理-收费项目列表）
        :return list: 
        :last_editors: HuangJianYi
        """

        project_code_list = []
        if not project_code:
            return project_code_list
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return project_code_list
        requst_url = "http://taobao-mp-s.gao7.com/general/project_code_list"
        data = {}
        data["project_code"] = project_code
        data["product_id"] = product_id
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = SevenHelper.json_loads(result.text)
            project_code_list = obj_data["Data"]
        return project_code_list

    def get_shop_config_list(self, store_user_nick):
        """
        :description:  获取店铺配置列表
        :param store_user_nick:商家主账号昵称
        :return list: 
        :last_editors: HuangJianYi
        """
        shop_config_list = []
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return shop_config_list
        requst_url = "http://taobao-mp-s.gao7.com/custom/query_skin_managemen_list"
        data = {}
        data["product_id"] = product_id
        data["store_user_nick"] = store_user_nick
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = SevenHelper.json_loads(result.text)
            shop_config_list = obj_data["Data"]
        return shop_config_list