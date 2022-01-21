# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-03 09:24:50
@LastEditTime: 2021-12-21 19:49:18
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *


class SkuInfoHandler(ClientBaseHandler):
    """
    :description: 获取SKU信息
    """
    def get_async(self):
        """
        :description: 获取SKU信息
        :param num_iid：num_iid
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False
        num_iid = self.get_param("num_iid")
        if not num_iid:
            num_iid = self.get_param("num_iids")
        if not num_iid:
            return self.response_json_error("param_error", "参数错误,缺少必传参数")
        top_base_model = TopBaseModel(context=self)
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list_by_goodsids(num_iid, app_info_dict["access_token"], app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if "items_seller_list_get_response" in invoke_result_data.data.keys():
            if "items" in invoke_result_data.data["items_seller_list_get_response"].keys():
                return self.response_json_success(invoke_result_data.data["items_seller_list_get_response"])
        else:
            act_prize = ActPrizeModel(context=self).get_dict("goods_id=%s and sku_json<>'' and is_sku=1 ", field="sku_json", params=[num_iid])
            if not act_prize:
                return self.response_json_error("error", "对不起，找不到该商品的sku")
            sku_detail = self.json_loads(act_prize['sku_json'])
            return self.response_json_success(sku_detail["items_seller_list_get_response"])


class GoodsListHandler(ClientBaseHandler):
    """
    :description: 获取商品列表
    """
    def get_async(self):
        """
        :description: 获取商品列表
        :param page_index：页索引
        :param page_size：页大小
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 10)
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        top_base_model = TopBaseModel(context=self)
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_goods_list(page_index, page_size, "", "", "", app_info_dict["access_token"], app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)
