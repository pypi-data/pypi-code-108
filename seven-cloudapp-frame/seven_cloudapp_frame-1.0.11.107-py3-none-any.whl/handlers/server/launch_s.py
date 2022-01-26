# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-30 15:46:34
@LastEditTime: 2021-11-29 16:39:08
@LastEditors: HuangJianYi
@Description: 投放模块
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.act_base_model import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.launch_base_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.launch.launch_goods_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *


class InitLaunchGoodsHandler(ClientBaseHandler):
    """
    :description: 初始化商品投放
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 初始化商品投放
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param source_types：商品来源，指定哪些位置的商品要进行投放（1活动奖品商品2价格档位商品） 多个逗号,分隔
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        source_types = self.get_param("source_types","1,2")

        online_url = self.get_online_url(act_id, app_id, module_id)
        launch_base_model = LaunchBaseModel(context=self)
        invoke_result_data = launch_base_model.init_launch_goods(app_id, act_id, source_types, online_url)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class ResetLaunchGoodsHandler(ClientBaseHandler):
    """
    :description: 重置商品投放 删除已投放的记录并将活动投放状态改为未投放
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 重置商品投放 删除已投放的记录并将活动投放状态改为未投放
        :param app_id：应用标识
        :param act_id：活动标识
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))

        ActInfoModel(context=self).update_table("is_launch=0", "app_id=%s and id=%s", params=[app_id, act_id])
        ActBaseModel(context=self)._delete_act_info_dependency_key(app_id, act_id)
        LaunchGoodsModel(context=self).del_entity("app_id=%s and id=%s", params=[app_id, act_id])
        return self.response_json_success()


class InitLaunchGoodsCallBackHandler(ClientBaseHandler):
    """
    :description: 初始化投放商品回调接口
    """
    def get_async(self):
        """
        :description: 初始化投放商品回调接口
        :param app_id：应用标识
        :param act_id：活动标识
        :param close_goods_id：投放失败时关闭投放的商品ID  多个逗号,分隔
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        close_goods_id = self.get_param("close_goods_id")

        ActInfoModel(context=self).update_table("is_launch=1", "id=%s", params=act_id)
        ActBaseModel(context=self)._delete_act_info_dependency_key(app_id,act_id)
        if close_goods_id != "":
            close_goods_id_list = list(set(close_goods_id.split(",")))
            LaunchGoodsModel(context=self).update_table("is_launch=0,launch_date=%s", "act_id=%s and "+ SevenHelper.get_condition_by_str_list("goods_id",close_goods_id_list), params=[SevenHelper.get_now_datetime(),act_id])

        return self.response_json_success()


class UpdateLaunchGoodsStatusHandler(ClientBaseHandler):
    """
    :description: 更改投放商品的状态
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 保存更改投放商品的状态
        :param app_id：应用标识
        :param 活动标识
        :param update_goods_id：更新商品ID（例：1）
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        goods_id = self.get_param("update_goods_id")
        if goods_id != "":
            LaunchGoodsModel(context=self).update_table("is_launch=abs(is_launch-1),is_sync=0,launch_date=%s", "app_id=%s and act_id=%s and goods_id=%s", [self.get_now_datetime(), app_id, act_id, goods_id])

        return self.response_json_success()


class LaunchGoodsListHandler(ClientBaseHandler):
    """
    :description: 投放商品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 投放商品列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :return 列表
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        launch_base_model = LaunchBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = launch_base_model.get_launch_goods_list(app_id, act_id, page_size, page_index, self.get_param("access_token"), app_key, app_secret)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class AsyncLaunchGoodsHandler(ClientBaseHandler):
    """
    :description: 同步投放商品（小程序投放-商品绑定/解绑）
    """
    @filter_check_params("app_id,act_id")
    def get_async(self):
        """
        :description: 同步投放商品（小程序投放-商品绑定/解绑）
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))

        online_url = self.get_online_url(act_id, app_id, module_id)
        launch_base_model = LaunchBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = launch_base_model.async_launch_goods(app_id, act_id, online_url, self.get_param("access_token"), app_key, app_secret)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()