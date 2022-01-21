# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-28 09:15:49
@LastEditTime: 2022-01-20 11:35:40
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.theme_base_model import *
from seven_cloudapp_frame.models.act_base_model import *


class ThemeInfoHandler(ClientBaseHandler):
    """
    :description: 获取主题（皮肤）信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取主题（皮肤）信息
        :param act_id：活动标识
        :param ver_no：客户端版本号
        :return 主题信息
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        ver_no = self.get_param("ver_no")

        act_base_model = ActBaseModel(context=self)
        act_info_dict = act_base_model.get_act_info_dict(act_id)
        if not act_info_dict:
            return self.response_json_error("no_act", "对不起，找不到该活动")
        theme_id = act_info_dict["theme_id"]
        theme_base_model = ThemeBaseModel(context=self)
        theme_info = theme_base_model.get_theme_info(theme_id, ver_no)
        return self.response_json_success(theme_info)


class SaveThemeHandler(ClientBaseHandler):
    """
    :description: 保存主题
    """
    @filter_check_params("out_id")
    def post_async(self):
        """
        :description: 保存主题
        :param app_id：应用标识
        :param theme_name：主题名称
        :param client_json：客户端内容json
        :param server_json：服务端内容json
        :param out_id：外部id
        :param ver_no：客户端版本号
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        theme_name = self.get_param("theme_name")
        client_json = self.get_param("client_json")
        server_json = self.get_param("server_json")
        out_id = self.get_param("out_id")
        ver_no = self.get_param("ver_no")
        style_type = int(self.get_param("style_type",0))

        theme_base_model = ThemeBaseModel(context=self)
        theme_base_model.save_theme(app_id, theme_name, client_json, server_json, out_id, ver_no, style_type)
        return self.response_json_success()


class SaveSkinHandler(ClientBaseHandler):
    """
    :description: 保存皮肤
    """
    @filter_check_params("theme_out_id,skin_out_id")
    def post_async(self):
        """
        :description: 保存皮肤
        :param app_id：应用标识
        :param skin_name：皮肤名称
        :param client_json：客户端内容json
        :param server_json：服务端内容json
        :param theme_out_id：样式外部id
        :param skin_out_id：皮肤外部id
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        skin_name = self.get_param("skin_name")
        client_json = self.get_param("client_json")
        server_json = self.get_param("server_json")
        theme_out_id = self.get_param("theme_out_id")
        skin_out_id = self.get_param("skin_out_id")
        style_type = self.get_param_int("style_type")

        theme_base_model = ThemeBaseModel(context=self)
        invoke_result_data = theme_base_model.save_skin(app_id, skin_name, client_json, server_json, theme_out_id, skin_out_id, style_type)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class ThemeInfoListHandler(ClientBaseHandler):
    """
    :description: 获取主题信息列表
    """
    def get_async(self):
        """
        :description: 保存皮肤
        :param app_id：应用标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        theme_base_model = ThemeBaseModel(context=self)
        return self.response_json_success(theme_base_model.get_theme_list(app_id))


class SkinInfoListHandler(ClientBaseHandler):
    """
    :description: 获取皮肤信息列表
    """
    @filter_check_params("theme_out_id")
    def get_async(self):
        """
        :description: 保存皮肤
        :param app_id：应用标识
        :return: 
        :last_editors: HuangJianYi
        """
        theme_out_id = self.get_param("theme_out_id")
        theme_base_model = ThemeBaseModel(context=self)
        return self.response_json_success(theme_base_model.get_skin_list(theme_out_id))