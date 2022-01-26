# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-28 09:54:51
@LastEditTime: 2022-01-21 21:28:11
@LastEditors: HuangJianYi
@Description: 
"""
from decimal import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.base.base_info_model import *
from seven_cloudapp_frame.models.db_models.friend.friend_link_model import *
from seven_cloudapp_frame.models.db_models.product.product_price_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_login_log_model import *
from seven_cloudapp_frame.models.db_models.version.version_info_model import *


class AppBaseModel():
    """
    :description: 应用信息业务模型
    """
    def __init__(self,context=None,logging_error=None,logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def get_app_id(self,store_name):
        """
        :description: 获取应用标识
        :param store_name:店铺名称
        :return app_id
        :last_editors: HuangJianYi
        """
        app_id = ""
        app_info_dict = AppInfoModel(context=self.context).get_cache_dict("store_name=%s", limit="1", field="app_id", params=[store_name])
        if app_info_dict:
            app_id = app_info_dict["app_id"]
        return app_id

    def get_app_info_dict(self,app_id,is_cache=True):
        """
        :description: 获取应用信息
        :param app_id: 应用标识
        :param is_cache: 是否缓存
        :return: 返回应用信息
        :last_editors: HuangJianYi
        """
        app_info_model = AppInfoModel(context=self.context)
        if is_cache:
            dependency_key = f"app_info:appid_{app_id}"
            return app_info_model.get_cache_dict(dependency_key=dependency_key, limit="1", where="app_id=%s", params=[app_id])
        else:
            return app_info_model.get_dict(where="app_id=%s", limit="1", params=[app_id])

    def get_app_expire(self,app_id):
        """
        :description: 获取小程序是否过期未续费
        :param app_id: 应用标识
        :return 1过期0未过期
        :last_editors: HuangJianYi
        """
        now_date = SevenHelper.get_now_datetime()
        invoke_result_data = InvokeResultData()
        app_info_dict = self.get_app_info_dict(app_id)
        if not app_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "小程序不存在"
            return invoke_result_data
        result = {}
        app_info_dict["expiration_date"] = str(app_info_dict["expiration_date"])
        if app_info_dict["expiration_date"] == "1900-01-01 00:00:00":
            result["is_expire"] = 0
        elif now_date > app_info_dict["expiration_date"]:
            result["is_expire"] = 1
        else:
            result["is_expire"] = 0
        invoke_result_data.data = result
        return invoke_result_data

    def get_left_navigation(self, user_nick, access_token, app_key, app_secret, app_id=""):
        """
        :description: 获取左侧导航
        :param user_nick: 用户昵称
        :param app_key: app_key
        :param app_secret: app_secret
        :param access_token: access_token
        :param app_id: 应用标识
        :return
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起，请先授权登录"
            return invoke_result_data
        base_info_dict = BaseInfoModel(context=self.context).get_dict()
        if not base_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "基础信息不存在"
            return invoke_result_data

        app_info_dict = None
        if app_id:
            app_info_dict = self.get_app_info_dict(app_id)

        # 左上角信息
        info = {}
        info["company"] = "天志互联"
        info["miniappName"] = base_info_dict["product_name"]
        info["logo"] = base_info_dict["product_icon"]
        info["client_now_ver"] = app_info_dict["template_ver"] if app_info_dict else ""

        # 左边底部菜单
        helper_info = {}
        helper_info["customer_service"] = base_info_dict["customer_service"]
        helper_info["video_url"] = base_info_dict["video_url"]
        helper_info["study_url"] = base_info_dict["study_url"]
        helper_info["is_remind_phone"] = base_info_dict["is_remind_phone"]
        helper_info["phone"] = ""

        # 过期时间
        renew_info = {}
        renew_info["surplus_day"] = 0
        dead_date = ""
        if app_info_dict:
            helper_info["phone"] = app_info_dict["app_telephone"]
            dead_date = app_info_dict["expiration_date"]
        else:
            top_base_model = TopBaseModel(context=self.context)
            invoke_result_data = top_base_model.get_dead_date(store_user_nick,access_token, app_key, app_secret)
            if invoke_result_data.success == False:
                return invoke_result_data
            dead_date = invoke_result_data.data
        renew_info["dead_date"] = dead_date
        if dead_date != "expire":
            renew_info["surplus_day"] = TimeHelper.difference_days(dead_date, SevenHelper.get_now_datetime())
        data = {}
        data["app_info"] = info
        data["helper_info"] = helper_info
        data["renew_info"] = renew_info

        product_price_model = ProductPriceModel(context=self.context)
        now_date = SevenHelper.get_now_datetime()
        product_price = product_price_model.get_cache_entity(where="%s>=begin_time and %s<=end_time and is_release=1",order_by="create_time desc",params=[now_date,now_date])
        base_info = {}
        # 把string转成数组对象
        base_info["update_function"] = SevenHelper.json_loads(base_info_dict["update_function"]) if base_info_dict["update_function"] else []
        base_info["update_function_b"] = SevenHelper.json_loads(base_info_dict["update_function_b"]) if base_info_dict["update_function_b"] else []
        base_info["decoration_poster_list"] = SevenHelper.json_loads(base_info_dict["decoration_poster_json"]) if base_info_dict["decoration_poster_json"] else []
        base_info["menu_config_list"] = SevenHelper.json_loads(base_info_dict["menu_config_json"]) if base_info_dict["menu_config_json"] else []
        base_info["product_price_list"] = SevenHelper.json_loads(product_price.content) if product_price else []
        base_info["server_ver"] = base_info_dict["server_ver"]
        base_info["is_force_update"] = base_info_dict["is_force_update"]
        #中台指定账号升级
        version_info = VersionInfoModel(context=self.context).get_entity(where="type_id=1",order_by="id desc")
        if version_info:
            if version_info.update_scope == 2 and version_info.white_lists:
                white_lists = list(set(str(version_info.white_lists).split(',')))
                if user_nick in white_lists:
                    base_info["client_ver"] = version_info.version_number
        #配置文件指定账号升级
        if user_nick:
            if user_nick == config.get_value("test_user_nick"):
                base_info["client_ver"] = config.get_value("test_client_ver")
        data["base_info"] = base_info
        invoke_result_data.data =data
        return invoke_result_data

    def get_app_info_result(self, user_nick, open_id, access_token, app_key, app_secret):
        """
        :description: 获取小程序信息
        :param user_nick:用户昵称
        :param open_id:open_id
        :param access_token: access_token
        :param app_key:app_key
        :param app_secret: app_secret
        :return app_info
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起，请先授权登录"
            return invoke_result_data
        if not open_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起，请先授权登录"
            return invoke_result_data

        app_info_model = AppInfoModel(context=self.context)
        app_info = app_info_model.get_entity("store_user_nick=%s", params=store_user_nick)
        top_base_model = TopBaseModel(context=self.context)
        invoke_result_data = top_base_model.get_dead_date(store_user_nick, access_token, app_key, app_secret)
        if invoke_result_data.success == False:
            return invoke_result_data
        dead_date = invoke_result_data.data
        now_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(TimeHelper.get_now_format_time('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S'))
        login_log = TaoLoginLogModel(context=self.context).get_entity("open_id=%s", order_by="id desc", params=open_id)
        if app_info:
            if dead_date != "expire":
                app_info.expiration_date = dead_date
            invoke_result_data = top_base_model.get_goods_list(0, 1, "", "", "", access_token, app_key, app_secret)
            if invoke_result_data.success == True:
                app_info.access_token = access_token
            app_info_model.update_entity(app_info,"expiration_date,access_token")
            app_info_model.delete_dependency_key(f"app_info:appid_{app_info.app_id}")

            app_info.user_nick = user_nick
            app_info.dead_date = dead_date
            if app_info.dead_date != "expire":
                dead_date_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(app_info.dead_date, '%Y-%m-%d %H:%M:%S'))
                app_info.surplus_day = int(int(abs(dead_date_timestamp - now_timestamp)) / 24 / 3600)
            app_info.last_login_date = login_log.modify_date if login_log else ""
            invoke_result_data.data = app_info
            return invoke_result_data
        else:
            app_info = AppInfo()
            app_info.access_token = access_token
            base_info = BaseInfoModel(context=self.context).get_dict(field="client_ver")

            app_info.template_ver = base_info["client_ver"]
            app_info.user_nick = user_nick
            app_info.dead_date = dead_date
            if app_info.dead_date != "expire":
                dead_date_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(app_info.dead_date, '%Y-%m-%d %H:%M:%S'))
                app_info.surplus_day = int(int(abs(dead_date_timestamp - now_timestamp)) / 24 / 3600)
            app_info.last_login_date = login_log.create_date if login_log else ""
            invoke_result_data.data = app_info
            return invoke_result_data
