# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-09 15:00:05
@LastEditTime: 2022-01-20 13:52:56
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.order_base_model import *
from seven_cloudapp_frame.models.stat_base_model import *


class HorseracelampListHandler(ClientBaseHandler):
    """
    :description: 获取跑马灯奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取跑马灯奖品列表
        :param act_id: 活动标识
        :param module_id: 活动模块标识
        :param page_size: 条数
        :param is_search_module: 是否查询活动模块
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", -1))
        page_size = int(self.get_param("page_size", 30))
        is_search_module = int(self.get_param("is_search_module", 0))
        if is_search_module == 0:
            is_search_module = False
        else:
            is_search_module = True

        if not app_id or not act_id:
            return self.response_json_success({"data": []})
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        condition = invoke_result_data.data["condition"] if invoke_result_data.data.__contains__("condition") else f"create_date>'{TimeHelper.add_hours_by_format_time(hour=-1)}'"
        params = invoke_result_data.data["params"] if invoke_result_data.data.__contains__("params") else []
        order_base_model = OrderBaseModel(context=self)
        horseracelamp_list = self.business_process_executed(order_base_model.get_horseracelamp_list(act_id, module_id, is_search_module, condition, params, page_size), ref_params={})
        return self.response_json_success(horseracelamp_list)


class SyncPayOrderHandler(ClientBaseHandler):
    """
    :description: 同步淘宝支付订单给用户加资产
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 同步淘宝支付订单给用户加资产
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        app_key, app_secret = self.get_app_key_secret()
        order_base_model = OrderBaseModel(context=self)
        asset_type = invoke_result_data.data["asset_type"] if invoke_result_data.data.__contains__("asset_type") else 3
        goods_id = invoke_result_data.data["goods_id"] if invoke_result_data.data.__contains__("goods_id") else ""
        sku_id = invoke_result_data.data["sku_id"] if invoke_result_data.data.__contains__("sku_id") else ""
        ascription_type = invoke_result_data.data["ascription_type"] if invoke_result_data.data.__contains__("ascription_type") else 1
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        invoke_result_data = order_base_model.sync_tao_pay_order(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, asset_type, goods_id, sku_id, ascription_type, app_key, app_secret, is_log, check_user_nick, continue_request_expire)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        ref_params["app_id"] = app_id
        ref_params["act_id"] = act_id
        ref_params["module_id"] = module_id
        ref_params["user_id"] = user_id
        ref_params["open_id"] = open_id

        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data:result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        stat_base_model = StatBaseModel(context=self)
        key_list_dict = {}
        key_list_dict["PayUserCount"] = 1
        key_list_dict["PayCount"] = result_data.data["pay_num"]
        key_list_dict["PayMoneyCount"] = result_data.data["pay_price"]
        stat_base_model.add_stat_list(ref_params["app_id"], ref_params["act_id"], ref_params["module_id"], ref_params["user_id"], ref_params["open_id"], key_list_dict)
        return result_data


class PrizeOrderListHandler(ClientBaseHandler):
    """
    :description: 用户奖品订单列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户奖品订单列表
        :param act_id：活动标识
        :param order_no：订单号
        :param tb_user_id：用户标识
        :param user_open_id：open_id
        :param order_status：订单状态（-1未付款-2付款中0未发货1已发货2不予发货3已退款4交易成功）
        :param create_date_start：订单创建时间开始
        :param create_date_end：订单创建时间结束
        :param page_size：页大小
        :param page_index：页索引
        :param order_by：排序
        :param is_search_roster：是否查询订单关联中奖记录
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        user_open_id = self.get_param("user_open_id")
        order_status = int(self.get_param("order_status",-10))
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        order_by = self.get_param("order_by","id desc")
        is_search_roster = int(self.get_param("is_search_roster", 0))
        if is_search_roster == 0:
            is_search_roster = False
        else:
            is_search_roster = True
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        condition = invoke_result_data.data["condition"] if invoke_result_data.data.__contains__("condition") else ""
        params = invoke_result_data.data["params"] if invoke_result_data.data.__contains__("params") else []
        order_by = invoke_result_data.data["order_by"] if invoke_result_data.data.__contains__("order_by") else "create_date desc"
        field = invoke_result_data.data["field"] if invoke_result_data.data.__contains__("field") else "*"
        prize_roster_sub_table = invoke_result_data.data["prize_roster_sub_table"] if invoke_result_data.data.__contains__("prize_roster_sub_table") else None

        order_base_model = OrderBaseModel(context=self)
        page_info = order_base_model.get_prize_order_list(app_id, act_id, user_id, user_open_id, "", "", "", "", "", order_status, create_date_start, create_date_end, page_size, page_index, order_by, field, is_search_roster=is_search_roster, is_cache=True, condition=condition, params=params, prize_roster_sub_table=prize_roster_sub_table)
        ref_params = {}
        page_info.data = self.business_process_executed(page_info.data, ref_params)
        return self.response_json_success(page_info)


class PrizeRosterListHandler(ClientBaseHandler):
    """
    :description: 用户中奖记录列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 用户中奖记录列表
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param order_no：订单号
        :param goods_type：物品类型（1虚拟2实物）
        :param prize_type：奖品类型(1现货2优惠券3红包4参与奖5预售)
        :param logistics_status：物流状态（0未发货1已发货2不予发货）
        :param prize_status：奖品状态（0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货）
        :param pay_status：支付状态(0未支付1已支付2已退款3处理中)
        :param page_size：页大小
        :param page_index：页索引
        :return PageInfo
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        user_id = self.get_user_id()
        order_no = self.get_param("order_no")
        goods_type = int(self.get_param("goods_type", -1))
        prize_type = int(self.get_param("prize_type", -1))
        logistics_status = int(self.get_param("logistics_status", -1))
        prize_status = int(self.get_param("prize_status", -1))
        pay_status = int(self.get_param("pay_status", -1))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})

        order_base_model = OrderBaseModel(context=self)
        page_info = order_base_model.get_prize_roster_list(app_id=app_id, act_id=act_id, module_id=module_id, user_id=user_id, open_id=open_id, order_no=order_no, goods_type=goods_type, prize_type=prize_type, logistics_status=logistics_status, prize_status=prize_status, pay_status=pay_status, page_size=page_size, page_index=page_index)
        ref_params = {}
        page_info.data = self.business_process_executed(page_info.data, ref_params)
        return self.response_json_success(page_info)


class SubmitSkuHandler(ClientBaseHandler):
    """
    :description: 中奖记录选择SKU提交
    """
    @filter_check_params("user_prize_id,sku_id")
    def get_async(self):
        """
        :description: 提交SKU
        :param user_prize_id：用户中奖信息标识
        :param sku_name：sku属性名称
        :param sku_id：sku_id
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        user_prize_id = int(self.get_param("user_prize_id"))
        sku_name = self.get_param("sku_name")
        sku_id = self.get_param("sku_id")

        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster = prize_roster_model.get_entity_by_id(user_prize_id)
        if not prize_roster or prize_roster.open_id != open_id or prize_roster.app_id != app_id:
            return self.response_json_error("no_user_prize", "对不起，找不到该奖品")
        if prize_roster.is_sku > 0:
            prize_roster.sku_id = sku_id
            prize_roster.sku_name = sku_name
            goods_code_list = self.json_loads(prize_roster.goods_code_list)
            goods_codes = [i for i in goods_code_list if str(i["sku_id"]) == sku_id]
            if goods_codes and len(goods_codes) > 0 and ("goods_code" in goods_codes[0].keys()):
                prize_roster.goods_code = goods_codes[0]["goods_code"]
        prize_roster_model.update_entity(prize_roster, "sku_id,sku_name,goods_code")

        return self.response_json_success()


class SelectPrizeOrderHandler(ClientBaseHandler):
    """
    :description: 中奖记录下单
    """
    @filter_check_params("act_id,tb_user_id,login_token,real_name,telephone")
    def get_async(self):
        """
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param login_token:用户访问令牌
        :param prize_ids:用户奖品id串，逗号分隔（为空则将所有未下单的奖品进行下单）
        :param real_name:用户名
        :param telephone:电话
        :param province:省
        :param city:市
        :param county:区县
        :param street:街道
        :param address:地址
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        login_token = self.get_param("login_token")
        prize_ids = self.get_param("prize_ids")
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")
        order_base_model = OrderBaseModel(context=self)
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        prize_ids = invoke_result_data.data["prize_ids"] if invoke_result_data.data.__contains__("prize_ids") else prize_ids
        invoke_result_data = order_base_model.select_prize_order(app_id, act_id, user_id, login_token, prize_ids, real_name, telephone, province, city, county, street,address)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        else:
            return self.response_json_success(self.business_process_executed(invoke_result_data, ref_params={}))