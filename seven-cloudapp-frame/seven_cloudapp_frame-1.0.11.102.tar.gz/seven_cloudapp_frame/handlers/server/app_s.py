# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-03 10:43:58
@LastEditTime: 2021-12-27 20:12:36
@LastEditors: HuangJianYi
@Description: 应用模块
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.app_base_model import *


class InstantiateAppHandler(ClientBaseHandler):
    """
    :description: 实例化小程序
    """
    def get_async(self):
        """
        :description: 实例化小程序
        :param app_id:应用标识
        :param user_nick:用户昵称
        :param access_token:access_token
        :param is_log：是否记录返回信息
        :return app_info
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        user_nick = self.get_user_nick()
        access_token = self.get_param("access_token")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        cache_key = f"instantiate:{user_nick}"
        if SevenHelper.is_continue_request(cache_key, 10000) == True:
            return self.response_json_error("error","操作太频繁,请10秒后再试")
        app_key, app_secret = self.get_app_key_secret()
        top_base_model = TopBaseModel(context=self)
        invoke_result_data = top_base_model.instantiate(app_id, user_nick, access_token, app_key, app_secret, is_log)
        SevenHelper.redis_init().delete(cache_key)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message,invoke_result_data.data)
        return self.response_json_success(invoke_result_data.data)


class UpdateTelephoneHandler(ClientBaseHandler):
    """
    :description: 更新手机号
    """
    @filter_check_params("telephone")
    def get_async(self):
        """
        :description: 更新手机号
        :param app_id:应用标识
        :param telephone：手机号
        :param check_code：验证码
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_open_id()
        app_id = self.get_app_id()
        telephone = self.get_param("telephone")
        check_code = self.get_param("check_code")
        modify_date = self.get_now_datetime()

        check_code_re = SevenHelper.redis_init().get("user_" + open_id + "_bind_phone_code")
        if check_code_re == None:
            return self.response_json_error("error", "验证码已过期")
        check_code_re = str(check_code_re, 'utf-8')
        if check_code != check_code_re:
            return self.response_json_error("error", "验证码错误")
        AppInfoModel(context=self).update_table("app_telephone=%s,modify_date=%s", "app_id=%s", [telephone, modify_date, app_id])
        return self.response_json_success()


class VersionUpgradeHandler(ClientBaseHandler):
    """
    :description: 前端版本更新
    """
    def get_async(self):
        """
        :description: 前端版本更新
        :param app_id:应用标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        access_token = self.get_param("access_token")
        user_nick = self.get_user_nick()
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        base_info = BaseInfoModel(context=self).get_entity()
        client_ver = base_info.client_ver

        #中台指定账号升级
        version_info = VersionInfoModel(context=self).get_entity(where="type_id=1",order_by="id desc")
        if version_info:
            if version_info.update_scope == 2 and version_info.white_lists:
                white_lists = list(set(str(version_info.white_lists).split(',')))
                if user_nick in white_lists:
                    client_ver = version_info.version_number

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.response_json_error("no_app", "小程序不存在")

        test_client_ver = config.get_value("test_client_ver")
        client_template_id = config.get_value("client_template_id")
        #配置文件指定账号升级
        if test_client_ver and user_nick == config.get_value("test_user_nick"):
            client_ver = test_client_ver
        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.version_upgrade(app_id, client_template_id, client_ver, access_token,app_key, app_secret, app_info, is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class AppInfoHandler(ClientBaseHandler):
    """
    :description: 获取小程序信息
    """
    @filter_check_params()
    def get_async(self):
        """
        :description: 获取小程序信息
        :return app_info
        :last_editors: HuangJianYi
        """
        app_base_model = AppBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = app_base_model.get_app_info_result(self.get_user_nick(), self.get_open_id(), self.get_param("access_token"), app_key, app_secret)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class GetAppIDHandler(ClientBaseHandler):
    """
    :description: 获取应用标识
    """
    @filter_check_params("store_name")
    def get_async(self):
        """
        :description: 获取应用标识
        :param store_name:店铺名称
        :return app_id
        :last_editors: HuangJianYi
        """
        store_name = self.get_param("store_name")
        app_base_model = AppBaseModel(context=self)
        return self.response_json_success(app_base_model.get_app_id(store_name))


class GetShortUrlHandler(ClientBaseHandler):
    """
    :description: 获取淘宝短链接
    """
    def get_async(self):
        """
        :description: 获取淘宝短链接
        :param url:链接地址
        :return: 
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False
        url = self.get_param("url")
        app_key, app_secret = self.get_app_key_secret()
        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_short_url(url, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return self.response_json_success("")
        else:
            return self.response_json_success(invoke_result_data.data)
