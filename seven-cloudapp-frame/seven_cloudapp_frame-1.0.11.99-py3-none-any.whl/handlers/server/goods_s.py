# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2021-08-03 10:11:39
@LastEditTime: 2021-12-21 19:52:47
@LastEditors: HuangJianYi
:description: 商品模块
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.goods_base_model import *


class GoodsListHandler(ClientBaseHandler):
    """
    :description: 商品列表（获取当前会话用户出售中的商品列表）
    """
    def get_async(self):
        """
        :description: 导入商品列表（获取当前会话用户出售中的商品列表）
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param page_index：页索引
        :param page_size：页大小
        :return: 列表
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        goods_name = self.get_param("goods_name")
        order_tag = self.get_param("order_tag", "list_time")
        order_by = self.get_param("order_by", "desc")
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 20)
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list(page_index, page_size, goods_name, order_tag, order_by, access_token, app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class GoodsListByGoodsIDHandler(ClientBaseHandler):
    """
    :description: 根据商品ID串获取商品列表
    """
    @filter_check_params("goods_ids")
    def get_async(self):
        """
        :description: 根据商品ID获取商品列表
        :param goods_ids：商品ID串，多个逗号,分隔
        :return: list
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        goods_ids = self.get_param("goods_ids")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list_by_goodsids(goods_ids, access_token, app_key,app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class GoodsInfoHandler(ClientBaseHandler):
    """
    :description: 获取商品信息
    """
    @filter_check_params("goods_id")
    def get_async(self):
        """
        :description: 获取商品信息
        :param goods_id：商品ID
        :return: 商品信息
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        goods_id = self.get_param("goods_id")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_info(goods_id, access_token, app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class BenefitDetailHandler(ClientBaseHandler):
    """
    :description: 获取优惠券详情信息
    """
    def get_async(self):
        """
        :description: 获取优惠券详情信息
        :param right_ename:奖池ID
        :return: dict
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        right_ename = self.get_param("right_ename")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.alibaba_benefit_query(right_ename, access_token,app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class InventoryGoodsListHandler(ClientBaseHandler):
    """
    :description: 导入商品列表（获取当前用户作为卖家的仓库中的商品列表）
    """
    def get_async(self):
        """
        :description: 导入商品列表（获取当前用户作为卖家的仓库中的商品列表）
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param page_index：页索引
        :param page_size：页大小
        :return: 列表
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        goods_name = self.get_param("goods_name")
        order_tag = self.get_param("order_tag", "list_time")
        order_by = self.get_param("order_by", "desc")
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 20)
        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = self.response_json_success(top_base_model.get_goods_inventory_list(page_index, page_size, goods_name, order_tag, order_by, access_token,app_key, app_secret))
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class SpecialGoodsListHandler(ClientBaseHandler):
    """
    :description: 专属下单商品列表
    """
    @filter_check_params("app_id")
    def get_async(self):
        """
        :description: 专属下单商品列表
        :param app_id：应用标识
        :param page_index：页索引
        :param page_size：页大小
        :param goods_name：商品名称
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        goods_name = self.get_param("goods_name")
        access_token = self.get_param("access_token")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        goods_base_model = GoodsBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = goods_base_model.get_special_goods_list(app_id, goods_name, access_token, app_key, app_secret, is_log, page_index, page_size)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class BindSpecialGoodsHandler(ClientBaseHandler):
    """
    :description: 专属下单商品绑定(单个商品)
    """
    @filter_check_params("goods_id")
    def get_async(self):
        """
        :description: 专属下单商品绑定(单个商品)
        :param goods_id：商品ID
        :param goods_name: 商品名称
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        access_token = self.get_param("access_token")
        goods_id = self.get_param("goods_id")
        goods_name = self.get_param("goods_name")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        goods_base_model = GoodsBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = goods_base_model.bind_special_goods(app_id, goods_id, goods_name, access_token, app_key, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()