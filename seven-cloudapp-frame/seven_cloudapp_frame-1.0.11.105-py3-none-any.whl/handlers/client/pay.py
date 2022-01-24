# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-13 16:49:46
@LastEditTime: 2022-01-22 11:46:41
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.libs.customize.seven_helper import SevenHelper
from seven_cloudapp_frame.libs.customize.wechat_helper import WeChatPayRequest, WeChatPayReponse, WeChatRefundReponse
from seven_cloudapp_frame.libs.customize.tiktok_helper import TikTokPayRequest, TikTokReponse
from seven_cloudapp_frame.models.shakeshop_base_model import *
from seven_cloudapp_frame.models.price_base_model import *
from seven_cloudapp_frame.models.asset_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.db_models.pay.pay_order_model import *
from seven_cloudapp_frame.models.db_models.refund.refund_order_model import *
from seven_cloudapp_frame.models.db_models.third.third_pay_order_model import *


class WechatVoucherOrderHandler(ClientBaseHandler):
    """
    :description: 创建微信预订单
    """
    @filter_check_params("user_id,pay_order_no")
    def get_async(self):
        """
        :description: 创建微信预订单
        :param pay_order_no:支付单号
        :param user_id:用户标识
        :return: 请求接口获取客户端需要的支付密钥数据
        :last_editors: HuangJianYi
        """
        user_id = self.get_user_id()
        pay_order_no = self.get_param("pay_order_no")
        invoke_result_data = InvokeResultData()

        if SevenHelper.is_continue_request(f"WechatVoucherOrderHandler_{str(user_id)}") == True:
            return self.response_json_error("error", "对不起,请求太频繁")
        pay_order_model = PayOrderModel(context=self)
        pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
        if not pay_order or pay_order.order_status != 0:
            return self.response_json_error("error", "抱歉!未查询到订单信息,请联系客服")
        pay_config = config.get_value("wechat_pay")
        pay_notify_url = pay_config["pay_notify_url"]

        # 商品说明
        body = pay_order.order_name
        # 金额
        total_fee = pay_order.pay_amount
        # ip
        ip = SevenHelper.get_first_ip(self.get_remote_ip())

        try:
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == True:
                pay_notify_url = invoke_result_data.data["pay_notify_url"] if invoke_result_data.data.__contains__("pay_notify_url") else pay_notify_url
                time_expire = invoke_result_data.data["time_expire"] if invoke_result_data.data.__contains__("time_expire") else str(SevenHelper.get_now_int(hours=1))  #交易结束时间,设置1小时
            invoke_result_data = WeChatPayRequest().create_order(pay_order_no, body, total_fee, ip, pay_notify_url, pay_order.open_id, time_expire)
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

            # self.logging_link_info('小程序支付返回前端参数:' + str(invoke_result_data.data))
            ref_params = {}
            invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
            return self.response_json_success(invoke_result_data.data)
        except Exception as ex:
            self.logging_link_error("【创建微信预订单异常】" + traceback.format_exc())
            return self.response_json_error("fail", "请重新支付")


class WechatPayNotifyHandler(FrameBaseHandler):
    """
    :description: 微信支付异步通知
    """
    @filter_check_params()
    def post_async(self):
        """
        :description:支付异步通知
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        xml_params = self.request.body.decode('utf-8')
        wechat_pay_reponse = None
        try:
            wechat_pay_reponse = WeChatPayReponse(xml_params)  # 创建对象
            response_result = wechat_pay_reponse.get_data()
            return_code = response_result["return_code"]
            result_code = response_result["result_code"]
            if return_code == "FAIL":
                return self.write(wechat_pay_reponse.convert_response_xml(response_result["return_msg"], False))
            if result_code == "FAIL":
                return self.write(wechat_pay_reponse.convert_response_xml(response_result["err_code_des"], False))
            if wechat_pay_reponse.check_sign() != True:  # 校验签名,成功则继续后续操作
                return self.write(wechat_pay_reponse.convert_response_xml("签名验证失败", False))
            total_fee = response_result["total_fee"]
            pay_order_no = response_result["out_trade_no"]

            pay_order_model = PayOrderModel(context=self)
            pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
            if not pay_order:
                return self.write(wechat_pay_reponse.convert_response_xml("未查询到订单信息", False))
            # 判断金额是否匹配
            if int(decimal.Decimal(str(pay_order.pay_amount)) * 100) != int(total_fee):
                self.logging_link_error(f"微信支付订单[{pay_order_no}] 金额不匹配疑似刷单.数据库金额:{str(pay_order.pay_amount)} 平台回调金额:{str(total_fee)}")
                return self.write(wechat_pay_reponse.convert_response_xml("金额异常", False))

            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(wechat_pay_reponse.convert_response_xml(invoke_result_data.error_message, False))
            ref_params = {}
            ref_params["pay_order"] = pay_order
            ref_params["response_result"] = response_result
            self.business_process_executed(invoke_result_data, ref_params)

            return self.write(wechat_pay_reponse.convert_response_xml("SUCCESS", True))

        except Exception as ex:
            self.logging_link_error("【微信支付异步通知】" + traceback.format_exc() + ":" + str(xml_params))
            return self.write(wechat_pay_reponse.convert_response_xml("数据异常", False))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        response_result = ref_params["response_result"]
        pay_order = ref_params["pay_order"]
        pay_order_model = PayOrderModel(context=self)
        transaction_id = response_result["transaction_id"]
        time_string = response_result["time_end"]
        if pay_order.order_status == 0 or pay_order.order_status == 2:
            pay_order.out_order_no = transaction_id
            pay_order.order_status = 1
            pay_order.pay_date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(time_string, "%Y%m%d%H%M%S"))
            pay_order_model.update_entity(pay_order, "out_order_no,order_status,pay_date")

        return result_data


class WechatRefundNotifyHandler(FrameBaseHandler):
    """
    :description: 微信退款异步通知
    """
    @filter_check_params()
    def post_async(self):
        invoke_result_data = InvokeResultData()
        xml_params = self.request.body.decode('utf-8')
        wechat_refund_reponse = None
        try:
            wechat_refund_reponse = WeChatRefundReponse(xml_params)  # 创建对象
            response_result = wechat_refund_reponse.get_data()
            return_code = response_result["return_code"]
            if return_code == "FAIL":
                return self.write(wechat_refund_reponse.convert_response_xml(response_result["return_msg"], False))
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(wechat_refund_reponse.convert_response_xml(invoke_result_data.error_message, False))
            # 解密
            req_info_dict = wechat_refund_reponse.decode_req_info(response_result["req_info"])
            req_info_dict = req_info_dict["root"]
            ref_params = {}
            ref_params["req_info_dict"] = req_info_dict
            self.business_process_executed(invoke_result_data, ref_params)
            return self.write(wechat_refund_reponse.convert_response_xml("SUCCESS", True))
        except Exception as ex:
            self.logging_link_error("【微信退款异步通知】" + traceback.format_exc() + ":" + str(xml_params))
            return self.write(wechat_refund_reponse.convert_response_xml("数据异常", False))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        req_info_dict = ref_params["req_info_dict"]
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        pay_order_model = PayOrderModel(db_transaction=db_transaction, context=self)
        refund_order_model = RefundOrderModel(db_transaction=db_transaction, context=self)
        try:
            db_transaction.begin_transaction()
            if req_info_dict["refund_status"] == "SUCCESS":
                self.logging_link_info(f'pay_order_no:{str(req_info_dict["out_trade_no"])},微信退款异步通知:' + str(req_info_dict))
                # 退款成功(相关表处理)
                refund_order_model.update_table("refund_status=3,out_refund_no=%s,refund_date=%s", where="refund_no=%s", params=[req_info_dict["refund_id"], req_info_dict["success_time"], req_info_dict["out_refund_no"]])
                pay_order_model.update_table("order_status=20,refund_amount=%s", where="pay_order_no=%s", params=[int(req_info_dict["settlement_refund_fee"]) / 100, req_info_dict["out_trade_no"]])
                db_transaction.commit_transaction()
            else:
                # 退款失败(只更新退款表)
                refund_order_model.update_table("refund_status=4", where="out_refund_no=%s", params=req_info_dict["refund_id"])
        except Exception as ex:
            db_transaction.rollback_transaction()
            self.logging_link_error("【微信退款异步通知数据处理异常】" + traceback.format_exc())

        return result_data


class TiktokVoucherOrderHandler(ClientBaseHandler):
    """
    :description: 创建抖音预订单
    """
    @filter_check_params("user_id,pay_order_no")
    def get_async(self):
        """
        :description: 创建抖音预订单
        :param pay_order_no:支付单号
        :param user_id:用户标识
        :return: 请求接口获取客户端需要的支付密钥数据
        :last_editors: HuangJianYi
        """
        user_id = self.get_user_id()
        pay_order_no = self.get_param("pay_order_no")
        invoke_result_data = InvokeResultData()

        if SevenHelper.is_continue_request(f"TiktokVoucherOrderHandler_{str(user_id)}") == True:
            return self.response_json_error("error", "对不起,请求太频繁")
        pay_order_model = PayOrderModel(context=self)
        pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
        if not pay_order or pay_order.order_status != 0:
            return self.response_json_error("error", "抱歉!未查询到订单信息,请联系客服")
        pay_config = config.get_value("tiktok_pay")
        pay_notify_url = pay_config["pay_notify_url"]
        # 商品描述
        subject = pay_order.order_name
        # 商品详情
        body = pay_order.order_desc
        # 金额
        total_amount = pay_order.pay_amount

        try:
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == True:
                pay_notify_url = invoke_result_data.data["pay_notify_url"] if invoke_result_data.data.__contains__("pay_notify_url") else pay_notify_url
                time_expire = invoke_result_data.data["time_expire"] if invoke_result_data.data.__contains__("time_expire") else 3600  #交易结束时间,设置1小时,单位秒
            invoke_result_data = TikTokPayRequest().create_order(pay_order_no=pay_order_no, notify_url=pay_notify_url, total_amount=total_amount, subject=subject, body=body, valid_time=time_expire)
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            # self.logging_link_info('小程序支付返回前端参数:' + str(invoke_result_data.data))
            pay_order_model.update_table("out_order_no=%s", "pay_order_no=%s", params=[invoke_result_data.data["order_id"], pay_order_no])
            ref_params = {}
            invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
            return self.response_json_success(invoke_result_data.data)
        except Exception as ex:
            self.logging_link_error("【创建抖音预订单异常】" + traceback.format_exc())
            return self.response_json_error("fail", "请重新支付")


class TiktokPayNotifyHandler(FrameBaseHandler):
    """
    :description: 抖音支付异步通知
    """
    @filter_check_params()
    def post_async(self):
        """
        :description:抖音支付异步通知
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        json_params = self.request.body.decode('utf-8')
        tiktok_reponse = None
        try:
            tiktok_reponse = TikTokReponse(json_params)
            response_result = tiktok_reponse.get_data()
            if tiktok_reponse.check_sign() != True:  # 校验签名,成功则继续后续操作
                return self.write(tiktok_reponse.convert_response_json(-1, "签名验证失败"))
            if response_result["type"] != "payment":
                return self.write(tiktok_reponse.convert_response_json(-1, "回调类型标记错误"))
            response_data = SevenHelper.json_loads(response_result["msg"])
            total_fee = response_data["total_amount"] if response_data.__contains__("total_amount") else 0
            pay_order_no = response_data["cp_orderno"]
            pay_order_model = PayOrderModel(context=self)
            pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
            if not pay_order:
                return self.write(tiktok_reponse.convert_response_json(-1, "未查询到支付订单信息"))
            # 判断金额是否匹配
            if int(decimal.Decimal(str(pay_order.pay_amount)) * 100) != int(total_fee):
                self.logging_link_error(f"抖音支付订单[{pay_order_no}] 金额不匹配疑似刷单.数据库金额:{str(pay_order.pay_amount)} 平台回调金额:{str(total_fee)}")
                return self.write(tiktok_reponse.convert_response_json(-1, "金额异常"))

            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(tiktok_reponse.convert_response_json(-1, invoke_result_data.error_message))

            ref_params = {}
            ref_params["pay_order"] = pay_order
            ref_params["response_data"] = response_data
            self.business_process_executed(invoke_result_data, ref_params)

            return self.write(tiktok_reponse.convert_response_json())

        except Exception as ex:
            self.logging_link_error("【抖音支付异步通知】" + traceback.format_exc() + ":" + str(json_params))
            return self.write(tiktok_reponse.convert_response_json(-1, "数据异常"))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        pay_order = ref_params["pay_order"]
        pay_order_model = PayOrderModel(context=self)
        if pay_order.order_status == 0 or pay_order.order_status == 2:
            pay_time = SevenHelper.get_now_datetime()
            order_id = ""
            tiktok_pay_request = TikTokPayRequest()
            query_invoke_result_data = tiktok_pay_request.query_order(pay_order.pay_order_no)
            if query_invoke_result_data.success == True:
                pay_time = query_invoke_result_data.data["payment_info"]["pay_time"]
                order_id = query_invoke_result_data.data["order_id"]
            pay_order.order_status = 1
            pay_order.pay_date = pay_time
            pay_order.out_order_no = order_id if order_id else pay_order.out_order_no
            pay_order_model.update_entity(pay_order, "out_order_no,order_status,pay_date")

        return result_data


class TiktokRefundNotifyHandler(FrameBaseHandler):
    """
    :description: 抖音退款异步通知
    """
    @filter_check_params()
    def post_async(self):
        invoke_result_data = InvokeResultData()
        json_params = self.request.body.decode('utf-8')
        tiktok_reponse = None
        try:
            tiktok_reponse = TikTokReponse(json_params)
            response_result = tiktok_reponse.get_data()
            if tiktok_reponse.check_sign() != True:  # 校验签名,成功则继续后续操作
                return self.write(tiktok_reponse.convert_response_json(-1, "签名验证失败"))
            if response_result["type"] != "refund":
                return self.write(tiktok_reponse.convert_response_json(-1, "回调类型标记错误"))
            response_data = SevenHelper.json_loads(response_result["msg"])
            cp_refundno = response_data["cp_refundno"]
            refund_order_model = RefundOrderModel(context=self)
            refund_order = refund_order_model.get_entity("refund_no=%s", params=[cp_refundno])
            if not refund_order:
                return self.write(tiktok_reponse.convert_response_json(-1, "未查询到退款订单信息"))
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(tiktok_reponse.convert_response_json(-1, invoke_result_data.error_message))
            ref_params = {}
            ref_params["refund_order"] = refund_order
            ref_params["response_data"] = response_data
            self.business_process_executed(invoke_result_data, ref_params)

            return self.write(tiktok_reponse.convert_response_json())

        except Exception as ex:
            self.logging_link_error("【抖音退款异步通知】" + traceback.format_exc() + ":" + str(json_params))
            return self.write(tiktok_reponse.convert_response_json(-1, "数据异常"))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        refund_order = ref_params["refund_order"]
        response_data = ref_params["response_data"]
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        pay_order_model = PayOrderModel(db_transaction=db_transaction, context=self)
        refund_order_model = RefundOrderModel(db_transaction=db_transaction, context=self)
        try:
            db_transaction.begin_transaction()
            if response_data["status"] == "SUCCESS":
                self.logging_link_info(f'refund_no:{str(response_data["cp_refundno"])},抖音退款异步通知:' + str(response_data))
                # 退款成功(相关表处理)
                refund_order_model.update_table("refund_status=3,refund_date=%s", where="refund_no=%s", params=[SevenHelper.get_now_datetime(), response_data["cp_refundno"]])
                pay_order_model.update_table("order_status=20,refund_amount=%s", where="pay_order_no=%s", params=[int(response_data["refund_amount"]) / 100, refund_order.pay_order_no])
                db_transaction.commit_transaction()
            else:
                # 退款失败(只更新退款表)
                refund_order_model.update_table("refund_status=4", where="refund_no=%s", params=[response_data["cp_refundno"]])
        except Exception as ex:
            db_transaction.rollback_transaction()
            self.logging_link_error("【抖音退款异步通知数据处理异常】" + traceback.format_exc())
        return result_data


class ShakeshopNotifyHandler(FrameBaseHandler):
    """
    :description: 抖店异步通知
    """
    def post_async(self):
        """
        :description:抖店异步通知
        :return: 
        :last_editors: HuangJianYi
        """
        result = None
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        asset_type = invoke_result_data.data["asset_type"] if invoke_result_data.data.__contains__("asset_type") else 3 #资产类型，默认价格档位
        goods_id = invoke_result_data.data["goods_id"] if invoke_result_data.data.__contains__("goods_id") else "" #商品id
        sku_id = invoke_result_data.data["sku_id"] if invoke_result_data.data.__contains__("sku_id") else "" #skuid
        reward_order_status_list = invoke_result_data.data["reward_order_status_list"] if invoke_result_data.data.__contains__("reward_order_status_list") else [2]  #订单奖励类型，默认2已支付
        sub_b_type_list = invoke_result_data.data["sub_b_type_list"] if invoke_result_data.data.__contains__("sub_b_type_list") else [] #下单场景，默认全部
        try:
            third_pay_order_model = ThirdPayOrderModel(context=self)
            user_info_model = UserInfoModel(context=self)
            shop_id = config.get_value("shake_shop")["shop_id"]
            app_key = config.get_value("shake_shop")["app_key"]
            app_secret = config.get_value("shake_shop")["app_secret"]
            shakeshop_base_model = ShakeShopBaseModel(self, app_key, app_secret, "SELF", None, shop_id)
            result = shakeshop_base_model.callback(self.request.headers, self.request.body, is_log=False)
            if result:
                result = result[0]
                result["data"] = json.loads(result["data"])
                if str(result["data"]["shop_id"]) != str(shop_id):
                    return self.write({'code': 0, 'msg': 'success'})
                tag = result.get('tag')
                if tag == '0':  # 抖店推送服务验证消息，需立即返回success
                    return self.write({'code': 0, 'msg': 'success'})
                if tag == '101':  # 订单支付成功，根据推送的消息参数进行必要的业务处理，5秒内返回success
                    params = {}
                    params["shop_order_id"] = result["data"]["p_id"] #店铺订单编号
                    order_detail_result = shakeshop_base_model.request(path="/order/orderDetail", params=params, is_log=False)
                    if order_detail_result and order_detail_result["code"] == 10000:
                        open_id = order_detail_result["data"]["shop_order_detail"]["open_id"]
                        user_info_dict = user_info_model.get_cache_dict("open_id=%s", limit="1", order_by="id desc", params=[open_id])
                        if user_info_dict:
                            tiktok_goods_id_list = []
                            if asset_type == 3:
                                price_base_model = PriceBaseModel(context=self.context)
                                price_gear_dict_list = price_base_model.get_price_gear_list(user_info_dict["app_id"], user_info_dict["act_id"], 100, 0).data
                                for price_gear_dict in price_gear_dict_list:
                                    tiktok_goods_id_list.append(price_gear_dict["goods_id"])
                            else:
                                tiktok_goods_id_list.append(str(goods_id))
                            pay_order_no_list, redis_init, pay_order_cache_key = self.get_pay_order_no_list(user_info_dict["app_id"], user_info_dict["user_id"])
                            third_pay_order_list = []
                            total_buy_num = 0
                            total_pay_price = 0
                            for sku_order in order_detail_result["data"]["shop_order_detail"]["sku_order_list"]:
                                asset_object_id = ""
                                if len(sub_b_type_list) > 0 and sku_order["sub_b_type"] not in sub_b_type_list:
                                    continue
                                if str(sku_order["product_id"]) in tiktok_goods_id_list and sku_order["order_status"] in reward_order_status_list and sku_order["order_id"] not in pay_order_no_list:
                                    if asset_type == 3:
                                        now_price_gear_dict = None
                                        for price_gear_dict in price_gear_dict_list:
                                            if (price_gear_dict["effective_date"] == '1900-01-01 00:00:00' or TimeHelper.format_time_to_datetime(price_gear_dict["effective_date"]) < TimeHelper.format_time_to_datetime(TimeHelper.timestamp_to_format_time(sku_order["pay_time"]))) and price_gear_dict["goods_id"] == str(sku_order["product_id"]):
                                                #关联类型：1商品skuid关联2商品id关联
                                                if price_gear_dict["relation_type"] == 1 and price_gear_dict["sku_id"] != str(sku_order["sku_id"]):
                                                    continue
                                                now_price_gear_dict = price_gear_dict
                                        if not now_price_gear_dict:
                                            continue
                                        asset_object_id = now_price_gear_dict["id"]
                                    else:
                                        if str(goods_id) != str(sku_order["product_id"]):
                                            continue
                                        if sku_id and str(sku_id) != str(sku_order["sku_id"]):
                                            continue
                                    third_pay_order = ThirdPayOrder()
                                    third_pay_order.app_id = user_info_dict["app_id"]
                                    third_pay_order.act_id = user_info_dict["act_id"]
                                    third_pay_order.user_id = user_info_dict["user_id"]
                                    third_pay_order.open_id = open_id
                                    third_pay_order.user_nick = user_info_dict["user_nick"]
                                    third_pay_order.goods_code = sku_order["product_id"]
                                    third_pay_order.goods_name = sku_order["product_name"]
                                    third_pay_order.order_status = sku_order["order_status"]
                                    third_pay_order.sku_id = sku_order["sku_id"]
                                    third_pay_order.sku_name = json.dumps(sku_order["spec"])
                                    third_pay_order.buy_num = sku_order["item_num"]
                                    third_pay_order.pay_price = decimal.Decimal(sku_order["pay_amount"] / 100)
                                    third_pay_order.main_pay_order_no = sku_order["parent_order_id"]
                                    third_pay_order.sub_pay_order_no = sku_order["order_id"]
                                    third_pay_order.pay_date = TimeHelper.timestamp_to_format_time(sku_order["pay_time"])
                                    third_pay_order.asset_type = asset_type
                                    third_pay_order.asset_object_id = asset_object_id
                                    third_pay_order.surplus_count = sku_order["item_num"]
                                    third_pay_order.create_date = SevenHelper.get_now_datetime()
                                    total_buy_num += int(sku_order["item_num"])
                                    total_pay_price += decimal.Decimal(sku_order["pay_amount"] / 100)
                                    third_pay_order_list.append(third_pay_order)
                            if len(third_pay_order_list) > 0:
                                third_pay_order_result = third_pay_order_model.add_list(third_pay_order_list)
                                if third_pay_order_result == True and total_buy_num > 0:
                                    #更新用户表
                                    user_info_model.update_table("pay_price=pay_price+%s,pay_num=pay_num+%s", "user_id=%s", params=[total_pay_price, total_buy_num, user_info_dict["user_id"]])
                                    asset_base_model = AssetBaseModel(context=self)
                                    for item in third_pay_order_list:
                                        only_id = str(item.sub_pay_order_no)
                                        asset_invoke_result_data = asset_base_model.update_user_asset(user_info_dict["app_id"], user_info_dict["act_id"], 0, user_info_dict["user_id"], user_info_dict["open_id"], user_info_dict["user_nick"], item.asset_type, item.buy_num, item.asset_object_id, 1, "", "", "抖店购买", only_id, self.__class__.__name__, self.request_code, info_json={})
                                        if asset_invoke_result_data.success == True:
                                            redis_init.lpush(pay_order_cache_key, item.sub_pay_order_no)
                                            redis_init.expire(pay_order_cache_key, 30 * 24 * 3600)
                                    self.business_process_executed(third_pay_order_list, ref_params={"total_buy_num": total_buy_num, "total_pay_price": total_pay_price, "sku_order_list": order_detail_result["data"]["shop_order_detail"]["sku_order_list"]})
                    else:
                        self.logging_link_info("【抖店异步通知结果】" + str(result) + ":" + str(order_detail_result))
                return self.write({'code': 0, 'msg': 'success'})
            else:
                return self.write({'code': 40041, 'message': '解析推送数据失败'})
        except Exception as ex:
            self.logging_link_error("【抖店异步通知】" + traceback.format_exc() + ":" + str(result))
            return self.write({'code': 40041, 'message': '解析推送数据失败'})

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        return result_data

    def get_pay_order_no_list(self,app_id,user_id):
        """
        :description: 获取已获取奖励的订单子编号列表
        :param app_id:应用标识
        :param user_id:用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        redis_init = SevenHelper.redis_init()
        pay_order_cache_key = f"sub_pay_order_no_list:appid_{app_id}_userid_{user_id}"
        pay_order_no_list = redis_init.lrange(pay_order_cache_key,0,-1)
        pay_order_list = []
        is_add = False
        if not pay_order_no_list or len(pay_order_no_list)<=0:
            third_pay_order_model = ThirdPayOrderModel(context=self)
            pay_order_list = third_pay_order_model.get_dict_list("app_id=%s and user_id=%s", field="sub_pay_order_no", params=[app_id, user_id])
            is_add = True
        if len(pay_order_list) >0:
            for item in pay_order_list:
                pay_order_no_list.append(item["sub_pay_order_no"])
                if is_add == True:
                    redis_init.lpush(pay_order_cache_key,item["sub_pay_order_no"])
                    redis_init.expire(pay_order_cache_key, 30 * 24 * 3600)
        return pay_order_no_list,redis_init,pay_order_cache_key