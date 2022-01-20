# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-10 11:29:31
@LastEditTime: 2022-01-11 10:34:38
@LastEditors: HuangJianYi
@Description: 处理数据统计上报
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.stat_base_model import *


class ShareReportHandler(ClientBaseHandler):
    """
    :description: 处理分享上报
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理分享上报
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        stat_base_model = StatBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        invoke_result_data = stat_base_model.process_share_report(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, check_user_nick, continue_request_expire, is_stat)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class InviteReportHandler(ClientBaseHandler):
    """
    :description: 处理邀请进入上报
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理邀请进入上报
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param invite_user_id:邀请人用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        from_user_id = int(self.get_param("invite_user_id", 0))
        open_id = self.get_param("open_id")
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        stat_base_model = StatBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        invoke_result_data = stat_base_model.process_invite_report(app_id, act_id, module_id, user_id, open_id, login_token, from_user_id, self.__class__.__name__, check_user_nick, continue_request_expire, is_stat)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)
