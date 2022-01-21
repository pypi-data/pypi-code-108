# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 13:51:10
@LastEditTime: 2022-01-06 10:32:57
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.push_base_model import *


class AppExpireHandler(ClientBaseHandler):
    """
    :description: 获取小程序是否过期未续费
    """
    def get_async(self):
        """
        :description: 获取小程序是否过期未续费
        :return info
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()

        app_base_model = AppBaseModel(context=self)
        invoke_result_data = app_base_model.get_app_expire(app_id)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class AddWechatSubscribeHandler(ClientBaseHandler):
    """
    :description: 添加微信订阅次数
    """
    def get_async(self):
        """
        :description: 添加微信订阅次数
        :return info
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()

        push_base_model = PushBaseModel(context=self)
        invoke_result_data = push_base_model.add_wechat_subscribe(app_id)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)