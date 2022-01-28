# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-17 11:19:05
@LastEditTime: 2022-01-28 10:57:09
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.task_base_model import *


class TaskInfoListHandler(ClientBaseHandler):
    """
    :description: 获取任务列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取任务列表
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param tb_user_id：用户标识
        :param task_types:任务类型 多个逗号,分隔
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        module_id = int(self.get_param("module_id", 0))
        task_types = self.get_param("task_types")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False
        task_base_model = TaskBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        daily_repeat_browse = invoke_result_data.data["daily_repeat_browse"] if invoke_result_data.data.__contains__("daily_repeat_browse") else False
        result_list,task_info_list,task_count_list = task_base_model.get_client_task_list(app_id, act_id, module_id, user_id, task_types, app_key, app_secret, is_log, daily_repeat_browse)
        ref_params = {}
        ref_params["task_info_list"] = task_info_list
        ref_params["task_count_list"] = task_count_list
        return self.response_json_success(self.business_process_executed(result_list, ref_params))


class ReceiveRewardHandler(ClientBaseHandler):
    """
    :description: 处理领取任务奖励
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理领取任务奖励
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :param task_id:任务标识
        :param task_sub_type:子任务类型
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        task_id = int(self.get_param("task_id", 0))
        task_sub_type = self.get_param("task_sub_type")
        task_base_model = TaskBaseModel(context=self)
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_new_user = invoke_result_data.data["check_new_user"] if invoke_result_data.data.__contains__("check_new_user") else False
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        info_json = invoke_result_data.data["info_json"] if invoke_result_data.data.__contains__("info_json") else None
        invoke_result_data = task_base_model.process_receive_reward(app_id, act_id, module_id, user_id, login_token, task_id, task_sub_type, self.__class__.__name__, self.request_code, check_new_user, check_user_nick, continue_request_expire, is_stat, info_json)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class FreeGiftHandler(ClientBaseHandler):
    """
    :description: 处理掌柜有礼、新人有礼、免费领取等相似任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理掌柜有礼、新人有礼、免费领取等相似任务
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
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_new_user = invoke_result_data.data["check_new_user"] if invoke_result_data.data.__contains__("check_new_user") else True
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        info_json = invoke_result_data.data["info_json"] if invoke_result_data.data.__contains__("info_json") else None
        invoke_result_data = task_base_model.process_free_gift(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, check_new_user, check_user_nick, continue_request_expire, is_stat, info_json)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class OneSignHandler(ClientBaseHandler):
    """
    :description: 处理单次签到任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理单次签到任务
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
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_new_user = invoke_result_data.data["check_new_user"] if invoke_result_data.data.__contains__("check_new_user") else False
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        info_json = invoke_result_data.data["info_json"] if invoke_result_data.data.__contains__("info_json") else {}
        invoke_result_data = task_base_model.process_one_sign(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, check_new_user, check_user_nick, continue_request_expire, is_stat, info_json)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class WeeklySignHandler(ClientBaseHandler):
    """
    :description: 处理每周签到任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理每周签到任务
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
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_new_user = invoke_result_data.data["check_new_user"] if invoke_result_data.data.__contains__("check_new_user") else False
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        info_json = invoke_result_data.data["info_json"] if invoke_result_data.data.__contains__("info_json") else None
        invoke_result_data = task_base_model.process_weekly_sign(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, check_new_user, check_user_nick, continue_request_expire, is_stat, info_json)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class CumulativeSignHandler(ClientBaseHandler):
    """
    :description: 处理累计签到任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理累计签到任务
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
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_new_user = invoke_result_data.data["check_new_user"] if invoke_result_data.data.__contains__("check_new_user") else False
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        info_json = invoke_result_data.data["info_json"] if invoke_result_data.data.__contains__("info_json") else None
        invoke_result_data = task_base_model.process_cumulative_sign(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, check_new_user, check_user_nick, continue_request_expire, is_stat,info_json)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class InviteNewUserHandler(ClientBaseHandler):
    """
    :description: 处理邀请新用户任务
    """
    @filter_check_params("act_id,tb_user_id,invite_user_id,login_token")
    def get_async(self):
        """
        :description: 处理邀请新用户任务
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
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        from_user_id = int(self.get_param("invite_user_id", 0))
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        check_new_user = invoke_result_data.data["check_new_user"] if invoke_result_data.data.__contains__("check_new_user") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        invoke_result_data = task_base_model.process_invite_new_user(app_id, act_id, module_id, user_id, login_token, from_user_id, self.__class__.__name__, check_user_nick, check_new_user, continue_request_expire)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class InviteJoinMemberHandler(ClientBaseHandler):
    """
    :description: 处理邀请加入会员任务
    """
    @filter_check_params("act_id,tb_user_id,invite_user_id,login_token")
    def get_async(self):
        """
        :description: 处理邀请加入会员任务
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
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        from_user_id = int(self.get_param("invite_user_id", 0))
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        app_key, app_secret = self.get_app_key_secret()
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        access_token = app_info_dict["access_token"] if app_info_dict else ""
        invoke_result_data = task_base_model.process_invite_join_member(app_id, act_id, module_id, user_id, login_token, from_user_id, self.__class__.__name__, access_token, app_key, app_secret, check_user_nick, continue_request_expire)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class CollectGoodsHandler(ClientBaseHandler):
    """
    :description: 处理收藏商品任务
    """
    @filter_check_params("act_id,tb_user_id,login_token,goods_id")
    def get_async(self):
        """
        :description: 处理收藏商品任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param goods_id:商品ID
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        module_id = int(self.get_param("module_id", 0))
        goods_id = self.get_param("goods_id")
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        invoke_result_data = task_base_model.process_collect_goods(app_id, act_id, module_id, user_id, login_token, goods_id, self.__class__.__name__, check_user_nick, continue_request_expire)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class BrowseGoodsHandler(ClientBaseHandler):
    """
    :description: 处理浏览商品任务
    """
    @filter_check_params("act_id,tb_user_id,login_token,goods_id")
    def get_async(self):
        """
        :description: 处理浏览商品任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param goods_id:商品ID
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        module_id = int(self.get_param("module_id", 0))
        goods_id = self.get_param("goods_id")
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        daily_repeat_browse = invoke_result_data.data["daily_repeat_browse"] if invoke_result_data.data.__contains__("daily_repeat_browse") else False
        invoke_result_data = task_base_model.process_browse_goods(app_id, act_id, module_id, user_id, login_token, goods_id, self.__class__.__name__, daily_repeat_browse, check_user_nick, continue_request_expire)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class FavorStoreHandler(ClientBaseHandler):
    """
    :description: 处理关注店铺
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理关注店铺
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
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        info_json = invoke_result_data.data["info_json"] if invoke_result_data.data.__contains__("info_json") else None
        invoke_result_data = task_base_model.process_favor_store(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, check_user_nick, continue_request_expire, is_stat, info_json)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class JoinMemberHandler(ClientBaseHandler):
    """
    :description: 处理加入店铺会员
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理加入店铺会员
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
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        info_json = invoke_result_data.data["info_json"] if invoke_result_data.data.__contains__("info_json") else None
        app_key, app_secret = self.get_app_key_secret()
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        access_token = app_info_dict["access_token"] if app_info_dict else ""
        invoke_result_data = task_base_model.process_join_member(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, access_token, app_key, app_secret, self.request_code, check_user_nick, continue_request_expire, is_stat, info_json)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class BrowseSiteHandler(ClientBaseHandler):
    """
    :description: 处理浏览网址相关任务 如：浏览店铺、浏览直播间、浏览会场/专题
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理浏览商品任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param task_type:任务类型
        :param task_sub_type:子任务类型
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        module_id = int(self.get_param("module_id", 0))
        task_type = int(self.get_param("task_type", 0))
        task_sub_type = self.get_param("task_sub_type")
        login_token = self.get_param("login_token")
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = InvokeResultData()
        if task_type not in [TaskType.browse_store.value,TaskType.browse_live_room.value,TaskType.browse_special_topic.value]:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "非法操作"
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        invoke_result_data = task_base_model.process_browse_site(app_id, act_id, module_id, user_id, login_token, task_type, task_sub_type, self.__class__.__name__, check_user_nick, continue_request_expire)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class ShareHandler(ClientBaseHandler):
    """
    :description: 分享奖励任务
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 分享奖励任务
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
        task_base_model = TaskBaseModel(context=self)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        check_new_user = invoke_result_data.data["check_new_user"] if invoke_result_data.data.__contains__("check_new_user") else False
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        invoke_result_data = task_base_model.process_share(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, check_new_user, check_user_nick, continue_request_expire)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)
