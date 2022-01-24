# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-18 17:42:13
@LastEditTime: 2022-01-21 21:29:06
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.seven_model import PageInfo
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.db_models.special.special_goods_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *

class GoodsBaseModel():
    """
    :description: 商品相关业务模型
    """
    def __init__(self,context=None,logging_error=None,logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def get_special_goods_list(self, app_id, goods_name, access_token, app_key, app_secret, is_log=False, page_index=0, page_size=20):
        """
        :description: 专属下单商品列表
        :param app_id：应用标识
        :param goods_name：商品名称
        :param access_tokene：access_token
        :param app_key：app_key
        :param app_secret：app_secret
        :param is_log：是否记录top请求日志
        :param page_index：页索引
        :param page_size：页大小
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        condition = "app_id=%s"
        params = [app_id]
        if goods_name:
            condition += " and goods_name=%s"
            params.append(goods_name)

        special_goods_model = SpecialGoodsModel(context=self.context)
        page_list, total = special_goods_model.get_dict_page_list("*", page_index, page_size, condition, params=params)
        if not page_list:
            invoke_result_data.data = []
            return invoke_result_data

        resp_special_goods = {}
        resp_on_sale_goods = {}
        act_prize_list = []
        goods_id_list = [str(special_goods["goods_id"]) for special_goods in page_list]
        if len(goods_id_list) > 0:
            goods_ids = ",".join(goods_id_list)
            act_prize_list = ActPrizeModel(context=self.context).get_dict_list(SevenHelper.get_condition_by_str_list("goods_id",goods_id_list))
            top_base_model = TopBaseModel(context=self.context)
            invoke_result_data = top_base_model.get_goods_list_by_goodsids(goods_ids, access_token, app_key, app_secret, is_log)
            if invoke_result_data.success == False:
                return invoke_result_data
            resp_on_sale_goods = invoke_result_data.data
            if "error_message" in resp_on_sale_goods.keys():
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = resp_on_sale_goods["error_message"]
                return invoke_result_data
            invoke_result_data = top_base_model.open_trade_special_items_query(app_id, access_token, app_key, app_secret, is_log)
            if invoke_result_data.success == False:
                return invoke_result_data
            resp_special_goods = invoke_result_data.data

        # resp_on_sale_goods = {'items_seller_list_get_response': {'items': {'item': [{'input_str': '123321', 'newprepay': 'default', 'nick': 'loveyouhk', 'num_iid': 645237589892, 'pic_url': 'https://img.alicdn.com/bao/uploaded/i4/305104024/O1CN01hjxRJe1fb2PfX01n8_!!305104024.jpg', 'price': '10.00', 'property_alias': '', 'props_name': '20000:6151601944:品牌:15phoe/衣窝风;20021:105255:主要材质:棉;20509:12430609:尺码:S（54-56cm）;1627207:28341:颜色分类:黑色;8560225:740132938:上市时间:2015年冬季;13021751:3251403:货号:123321', 'skus': {'sku': [{'created': '2021-05-23 16:00:15', 'modified': '2021-05-23 16:00:15', 'price': '10.00', 'properties': '20509:12430609;1627207:28341', 'properties_name': '20509:12430609:尺码:S（54-56cm）;1627207:28341:颜色分类:黑色', 'quantity': 10, 'sku_id': 4818446850738}]}, 'title': '专属测试523男士包头帽'}, {'input_str': '', 'newprepay': 'default', 'nick': 'loveyouhk', 'num_iid': 645938651976, 'pic_url': 'https://img.alicdn.com/bao/uploaded/i4/305104024/O1CN01hjxRJe1fb2PfX01n8_!!305104024.jpg', 'price': '10.00', 'property_alias': '', 'props_name': '20021:105255:主要材质:棉', 'title': '523170000'}]}, 'request_id': '41zzkkd2aorh'}}
        # resp_special_goods = {'opentrade_special_items_query_response': {'items': {'number': [645938651976, 645237589892, 634388910274, 641313416583, 641692061394, 641691601551, 632998091188, 639914960755]}, 'request_id': '5aaavqza0p93'}}

        for special_goods in page_list:
            if "items_seller_list_get_response" in resp_on_sale_goods.keys():
                if "items" in resp_on_sale_goods["items_seller_list_get_response"].keys():
                    cur_resp_goods_list = [resp_goods for resp_goods in resp_on_sale_goods["items_seller_list_get_response"]["items"]["item"] if resp_goods["num_iid"] == special_goods["goods_id"]]
                    if len(cur_resp_goods_list) > 0:
                        special_goods["title"] = cur_resp_goods_list[0]["title"]
                        special_goods["price"] = cur_resp_goods_list[0]["price"]
                    else:
                        special_goods["title"] = ""
                        special_goods["price"] = 0.00

                    if special_goods["title"] != "" and special_goods["title"] != special_goods["goods_name"]:
                        special_goods_model.update_table("goods_name=%s", "id=%s", params=[special_goods["title"], special_goods["id"]])

            if "opentrade_special_items_query_response" in resp_special_goods.keys():
                if "items" in resp_special_goods["opentrade_special_items_query_response"].keys():
                    cur_resp_special_goods_list = [goods_id for goods_id in resp_special_goods["opentrade_special_items_query_response"]["items"]["number"] if goods_id == special_goods["goods_id"]]
                    if len(cur_resp_special_goods_list) <= 0:
                        special_goods["is_bind"] = 1
                    else:
                        special_goods["is_bind"] = 0

            cur_act_prize_list = [act_prize for act_prize in act_prize_list if act_prize["goods_id"] == special_goods["goods_id"]]
            special_goods["is_select"] = 1 if len(cur_act_prize_list) > 0 else 0

        page_info = PageInfo(page_index, page_size, total, page_list)
        invoke_result_data.data = page_info
        return invoke_result_data

    def bind_special_goods(self, app_id, goods_id, goods_name, access_token, app_key, app_secret, is_log=False):
        """
        :description: 专属下单商品绑定(单个商品)
        :param app_id：应用标识
        :param goods_id：商品ID
        :param goods_name: 商品名称
        :param access_tokene：access_token
        :param app_key：app_key
        :param app_secret：app_secret
        :param is_log：是否记录top请求日志
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        top_base_model = TopBaseModel(context=self.context)
        invoke_result_data = top_base_model.open_trade_special_items_bind(app_id, goods_id, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return invoke_result_data
        special_goods_model = SpecialGoodsModel()
        special_goods = special_goods_model.get_dict("app_id=%s and goods_id=%s", limit="1", params=[app_id, goods_id])
        if not special_goods:
            special_goods = SpecialGoods()
            special_goods.app_id = app_id
            special_goods.goods_id = goods_id
            special_goods.goods_name = goods_name
            special_goods.create_date = SevenHelper.get_now_datetime()
            special_goods_model.add_entity(special_goods)
        else:
            special_goods.goods_id = goods_id
            special_goods.goods_name = goods_name
            special_goods.modify_date = SevenHelper.get_now_datetime()
            special_goods_model.update_entity(special_goods,"goods_id,goods_name,modify_date")
        return invoke_result_data
