# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-19 09:23:14
@LastEditTime: 2022-01-10 13:57:25
@LastEditors: HuangJianYi
@Description: 
"""
from time import *
from requests_pkcs12 import post
import requests
from Crypto.Cipher import AES
import base64
import xmltodict
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
from urllib.parse import quote
import hashlib
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_framework.base_model import *
from seven_cloudapp_frame.models.seven_model import InvokeResultData


class WeChatHelper:
    """
    :description: 微信帮助类 1.临时登录凭证校验获取open_id、session_key  2.解析加密数据
    """
    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def code2_session(self, code, grant_type="authorization_code",app_id="", app_secret=""):
        """
        :description:临时登录凭证校验
        :param code：登录票据
        :param grant_type：授权方式
        :param app_id：app_id
        :param app_secret：app_secret
        :return: 返回字典包含字段 session_key,openid
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")
        app_secret = app_secret if app_secret else config.get_value("app_secret")
        invoke_result_data = InvokeResultData()
        redis_key = f"{app_id}_wechat_login_code:{str(code)}"
        redis_init = SevenHelper.redis_init()
        code2_session_dict = redis_init.get(redis_key)
        if code2_session_dict:
            code2_session_dict = SevenHelper.json_loads(code2_session_dict)
            invoke_result_data.data = code2_session_dict
            return invoke_result_data
        param = {
            'js_code': code,  # 用户点击按钮跳转到微信授权页, 微信处理完后重定向到redirect_uri, 并给我们加上code=xxx的参数, 这个code就是我们需要的
            'appid': app_id,
            'secret': app_secret,
            'grant_type': grant_type,
        }

        # 通过code获取access_token
        requset_url = 'https://api.weixin.qq.com/sns/jscode2session'
        response = None
        try:
            response = requests.get(requset_url, params=param)
            response_data = SevenHelper.json_loads(response.text)
            if response_data.__contains__("errcode") and response_data["errcode"] != 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = response_data["errcode"]
                invoke_result_data.error_message = response_data["errmsg"]
                return invoke_result_data
            open_id = response_data['openid']
            session_key = response_data['session_key']
            redis_init.set(redis_key, SevenHelper.json_dumps(response_data), ex=60 * 60)
            redis_init.set(f"{app_id}_wechat_sessionkey:{open_id}", session_key, ex=60 * 60)
            invoke_result_data.data = response_data
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【code2_session】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = traceback.format_exc()
            return invoke_result_data

    @classmethod
    def get_access_token(self, grant_type="client_credential",app_id="", app_secret=""):
        """
        :description:access_token 是小程序的全局唯一调用凭据，开发者调用小程序支付时需要使用 access_token。access_token 的有效期为 2 个小时，需要定时刷新 access_token，重复获取会导致之前一次获取的 access_token 的有效期缩短为 5 分钟。
        :param grant_type: 获取access_token 时值为 client_credential
        :param app_id:app_id
        :param app_secret:app_secret
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")
        app_secret = app_secret if app_secret else config.get_value("app_secret")

        invoke_result_data = InvokeResultData()
        param = {
            'appid': app_id,
            'secret': app_secret,
            'grant_type': grant_type,
        }
        response = None
        redis_init = SevenHelper.redis_init()
        redis_key = f"wechat_access_token:{str(app_id)}"
        try:
            access_token = redis_init.get(redis_key)
            if access_token:
                invoke_result_data.data = access_token
                return invoke_result_data
            requset_url = 'https://api.weixin.qq.com/cgi-bin/token'
            response = requests.get(requset_url, params=param)
            response_data = SevenHelper.json_loads(response.text)
            if response_data.__contains__("errcode") and response_data["errcode"] != 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = response_data["errcode"]
                invoke_result_data.error_message = response_data["errmsg"]
                return invoke_result_data
            invoke_result_data.data = str(response_data["access_token"])
            redis_init.set(redis_key, invoke_result_data.data, ex=3600)
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【get_access_token】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = traceback.format_exc()
            return invoke_result_data

    @classmethod
    def send_template_message(self, open_id, template_id, page, request_data, miniprogram_state="formal", lang="zh_CN", app_id="", app_secret=""):
        """
        :description:发送订阅消息（https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/subscribe-message/subscribeMessage.send.html）
        :param open_id:接收者（用户）的 openid
        :param template_id:所需下发的订阅模板id
        :param page:点击模板卡片后的跳转页面，仅限本小程序内的页面。支持带参数,（示例index?foo=bar）。该字段不填则模板无跳转
        :param request_data:模板内容，格式形如 { “date2”: { “value”: any }, “thing3”: { “value”: any } }
        :param miniprogram_state:跳转小程序类型：developer为开发版；trial为体验版；formal为正式版；默认为正式版
        :param lang:进入小程序查看”的语言类型，支持zh_CN(简体中文)、en_US(英文)、zh_HK(繁体中文)、zh_TW(繁体中文)，默认为zh_CN
        :param app_id:app_id
        :param app_secret:app_secret
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")
        app_secret = app_secret if app_secret else config.get_value("app_secret")
        invoke_result_data = self.get_access_token(app_id,app_secret)
        if invoke_result_data.success == False:
            return invoke_result_data
        try:
            requset_url = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send'
            param = {
                "touser": open_id,
                "page": page,
                "lang": lang,
                "data": request_data,
                "templateId": template_id,
                "miniprogramState": miniprogram_state
                }
            respone = requests.post(url=requset_url,params={'access_token': invoke_result_data.data},data=json.dumps(param, ensure_ascii=False).encode('utf-8'))
            respone_data = SevenHelper.json_loads(respone.text)
            if respone_data.__contains__("errcode") and respone_data["errcode"] != 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = respone_data["errcode"]
                invoke_result_data.error_message = respone_data["errmsg"]
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【send_template_message】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = traceback.format_exc()
            return invoke_result_data
        return invoke_result_data

    @classmethod
    def decrypt_data_by_code(self, open_id, code, encrypted_Data, iv, app_id="", app_secret=""):
        """
        :description:解析加密数据，客户端判断是否登录状态，如果登录只传open_id不传code，如果是登录过期,要传code重新获取session_key
        :param open_id：open_id
        :param code：登录票据
        :param encrypted_Data：加密数据,微信返回加密参数
        :param iv：微信返回参数
        :param app_id：app_id
        :param app_secret：app_secret
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")
        app_secret = app_secret if app_secret else config.get_value("app_secret")

        data = None
        if code:
            code2_session_dict = self.code2_session(code=code, app_id=app_id, app_secret=app_secret)
            if code2_session_dict:
                open_id = code2_session_dict["openid"]
        try:
            session_key = SevenHelper.redis_init().get(f"{app_id}_wechat_sessionkey:{open_id}")
            wx_data_crypt = WeChatDataCrypt(app_id, session_key)
            data = wx_data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error("【decrypt_data_by_code】" + traceback.format_exc())
        return data

    @classmethod
    def decrypt_data(self, session_key, encrypted_Data, iv, app_id=""):
        """
        :description:解析加密数据
        :param session_key: session_key调用登录接口获得
        :param encrypted_Data：加密数据,微信返回加密参数
        :param iv：微信返回参数
        :param app_id: 微信小程序标识
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")

        data = {}
        try:
            wx_data_crypt = WeChatDataCrypt(app_id, session_key)
            data = wx_data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error("【decrypt_data】" + traceback.format_exc())
        return data

    @classmethod
    def array_to_xml(self, array):
        """
        :description:array转xml
        :return:
        :last_editors: HuangJianYi
        """
        xml = ["<xml>"]
        for k, v in array.items():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    @classmethod
    def xml_to_array(self, xml):
        """
        :description:将xml转为array
        :return:
        :last_editors: HuangJianYi
        """
        array_data = {}
        root = ElementTree.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data

    @classmethod
    def key_value_url(self, params, url_encode):
        """
        :description:   将键值对转为 key1=value1&key2=value2 对参数按照key=value的格式，并按照参数名ASCII字典序排序
        :param params：参数字典
        :param url_encode：是否url编码 True是False否
        :return: 
        :last_editors: HuangJianYi
        """
        slist = sorted(params)
        buff = []
        for k in slist:
            v = quote(params[k]) if url_encode else params[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    @classmethod
    def get_nonce_str(self, length=32):
        """
        :description: 生成随机字符串
        :param length：长度
        :return: 
        :last_editors: HuangJianYi
        """
        import random
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)

    @classmethod
    def get_sign(self, params, api_key):
        """
        :description:生成sign拼接API密钥
        :param api_key: api密钥
        :return: 
        :last_editors: HuangJianYi
        """
        string_a = WeChatHelper.key_value_url(params, False)
        string_sign_temp = string_a + '&key=' + api_key  # APIKEY, API密钥，需要在商户后台设置
        sign = (hashlib.md5(string_sign_temp.encode("utf-8")).hexdigest()).upper()
        return sign


class WeChatPayRequest(object):
    """
    :description: 微信支付请求类,配置文件内容 "wechat_pay": {"api_key": "","mch_id": "","certificate_url":""}
    """
    """配置账号信息"""
    # =======【基本信息设置】=====================================
    # 微信公众号身份的唯一标识。审核通过后，在微信发送的邮件中查看
    app_id = ""
    # 受理商ID，身份标识
    mch_id = ""
    # API密钥，需要在商户后台设置
    api_key = ""
    # 证书地址,证书文件需要在商户后台下载
    certificate_url = ""

    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, app_id="", api_key="", mch_id="", certificate_url=""):
        pay_config = config.get_value("wechat_pay")
        self.app_id = app_id if app_id else config.get_value("app_id")
        self.api_key = api_key if api_key else pay_config["api_key"]
        self.mch_id = mch_id if mch_id else pay_config["mch_id"]
        self.certificate_url = certificate_url if certificate_url else pay_config["certificate_url"]

    def get_prepay_id(self, unified_order_url, params):
        """
        :description: 获取预支付单号prepay_id
        :param unifiedorder_url：微信下单地址
        :param params：请求参数字典
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        redis_key = f"{self.app_id}_wechat_prepay_id:" + str(params['out_trade_no'])
        redis_init = SevenHelper.redis_init()
        prepay_id = redis_init.get(redis_key)
        if prepay_id:
            invoke_result_data.data = prepay_id
            return invoke_result_data
        params['sign'] = WeChatHelper.get_sign(params, self.api_key)
        respone = requests.post(unified_order_url, self.convert_request_xml(params), headers={'Content-Type': 'application/xml'})
        response_data = xmltodict.parse(respone.text.encode('ISO-8859-1').decode('utf-8'))['xml']
        if response_data['return_code'] == 'SUCCESS':
            if response_data['result_code'] == 'SUCCESS':
                prepay_id = str(response_data['prepay_id'])
                redis_init.set(redis_key, prepay_id, ex=3600 * 1)
                invoke_result_data.data = prepay_id
                return invoke_result_data
            else:
                self.logger_error.error("【预支付单号】" + str(response_data))
                invoke_result_data.success = False
                invoke_result_data.error_code="error"
                invoke_result_data.error_message = response_data['err_code_des']
                return invoke_result_data
        else:
            self.logger_error.error("【预支付单号】" + str(response_data))
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = response_data['return_msg']
            return invoke_result_data

    def create_order(self, pay_order_no, body, total_fee, spbill_create_ip, notify_url, open_id="", time_expire="", trade_type="JSAPI"):
        """
        :description: 创建微信预订单
        :param pay_order_no：商户订单号(支付单号)
        :param body：订单描述
        :param total_fee：支付金额；单位元
        :param spbill_create_ip：客户端IP
        :param notify_url：微信支付结果异步通知地址
        :param open_id：微信open_id
        :param time_expire：交易结束时间
        :param trade_type：交易类型trade_type为JSAPI时，openid为必填参数！此参数为微信用户在商户对应appid下的唯一标识, 统一支付接口中，缺少必填参数openid！
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        spbill_create_ip = spbill_create_ip if SevenHelper.is_ip(spbill_create_ip) == True else "127.0.0.1"
        params = {
            'appid': self.app_id,  # appid
            'mch_id': self.mch_id,  # 商户号
            'nonce_str': WeChatHelper.get_nonce_str(),
            'body': body,
            'out_trade_no': str(pay_order_no),
            'total_fee': str(int(decimal.Decimal(str(total_fee)) * 100)),
            'spbill_create_ip': spbill_create_ip,
            'trade_type': trade_type,
            'notify_url': notify_url
        }
        if trade_type == "JSAPI":
            if open_id == "":
                invoke_result_data.success = False
                invoke_result_data.error_code="error"
                invoke_result_data.error_message = "缺少必填参数open_id"
                return invoke_result_data
            else:
                params['openid'] = open_id
        if time_expire != "":
            params['time_expire'] = str(time_expire)

        # 开发者调用支付统一下单API生成预交易单
        unified_order_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        invoke_result_data = self.get_prepay_id(unified_order_url, params)
        if invoke_result_data.success == False:
            return invoke_result_data
        prepay_id = invoke_result_data.data
        params['prepay_id'] = prepay_id
        params['package'] = f"prepay_id={prepay_id}"
        params['timestamp'] = str(int(time.time()))
        sign_again_params = {'appId': params['appid'], 'nonceStr': params['nonce_str'], 'package': params['package'], 'signType': 'MD5', 'timeStamp': params['timestamp']}
        sign_again_params['sign'] = WeChatHelper.get_sign(sign_again_params, self.api_key)
        invoke_result_data.data = sign_again_params
        return invoke_result_data  # 返回给app

    def query_order(self, pay_order_no="", transaction_id=""):
        """
        :description: 查询订单
        :param transaction_id：微信订单号
        :param pay_order_no：商户订单号(支付单号)
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if transaction_id == "" and pay_order_no == "":
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "缺少必填参数transaction_id或pay_order_no"
            return invoke_result_data
        request_xml = ""
        try:
            params = {
                'appid': self.app_id,
                'mch_id': self.mch_id,
                'nonce_str': WeChatHelper.get_nonce_str(),
            }
            if transaction_id != "":
                params['transaction_id'] = str(transaction_id)
            if pay_order_no != "":
                params['out_trade_no'] = str(pay_order_no)
            params['sign'] = WeChatHelper.get_sign(params, self.api_key)
            request_xml = self.convert_request_xml(params)
            queryorder_url = 'https://api.mch.weixin.qq.com/pay/orderquery'
            respone = requests.post(queryorder_url, request_xml, headers={'Content-Type': 'application/xml'})
            response_data = xmltodict.parse(respone.text.encode('ISO-8859-1').decode('utf-8'))['xml']
            invoke_result_data.data = response_data
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【查询订单】" + traceback.format_exc() + ":" + str(request_xml))
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "查询订单出现异常"
            return invoke_result_data

    def close_order(self, pay_order_no=""):
        """
        :description: 关闭订单
        :param pay_order_no：商户订单号(支付单号)
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if pay_order_no == "":
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "缺少必填参数pay_order_no"
            return invoke_result_data
        request_xml = ""
        try:
            params = {
                'appid': self.app_id,
                'mch_id': self.mch_id,
                'nonce_str': WeChatHelper.get_nonce_str(),
                'out_trade_no': str(pay_order_no)
            }
            params['sign'] = WeChatHelper.get_sign(params, self.api_key)
            request_xml = self.convert_request_xml(params)
            queryorder_url = 'https://api.mch.weixin.qq.com/pay/closeorder'
            respone = requests.post(queryorder_url, request_xml, headers={'Content-Type': 'application/xml'})
            response_data = xmltodict.parse(respone.text.encode('ISO-8859-1').decode('utf-8'))['xml']
            invoke_result_data.data = response_data
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【关闭订单】" + traceback.format_exc() + ":" + str(request_xml))
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "关闭订单出现异常"
            return invoke_result_data

    def get_pay_status(self, pay_order_no, transaction_id=""):
        """
        :description: 查询订单状态
        :param pay_order_no：商户订单号(支付单号)
        :param transaction_id：微信订单号
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data = self.query_order(pay_order_no, transaction_id)
        if invoke_result_data.success == False:
            return ""
        else:
            response_data = invoke_result_data.data
            if response_data['return_code'] == 'SUCCESS':
                if response_data['result_code'] == 'SUCCESS':
                    return str(response_data['trade_state'] if response_data.__contains__("trade_state") else "")  # SUCCESS--支付成功REFUND--转入退款NOTPAY--未支付CLOSED--已关闭REVOKED--已撤销(刷卡支付)USERPAYING--用户支付中PAYERROR--支付失败(其他原因，如银行返回失败)ACCEPT--已接收，等待扣款
                else:
                    return ""
            else:
                return ""

    def create_refund(self, refund_no, pay_order_no, notify_url, refund_fee, total_fee):
        """
        :description: 服务端退款请求
        :param refund_no:开发者侧的退款单号, 不可重复
        :param pay_order_no:商户分配订单号，标识进行退款的订单，开发者服务端的唯一订单号
        :param notify_url:退款通知地址
        :param refund_fee: 退款金额，单位[分]
        :param total_fee：支付金额；单位元
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        params = {
            'appid': self.app_id,  # appid
            'mch_id': self.mch_id,  # 商户号
            'nonce_str': WeChatHelper.get_nonce_str(),
            'out_trade_no': str(pay_order_no),
            'out_refund_no': str(refund_no),
            'notify_url': notify_url,
            'refund_fee': int(decimal.Decimal(str(refund_fee)) * 100),
            'sign_type': 'MD5',
            'total_fee': int(decimal.Decimal(str(total_fee)) * 100),
        }
        params['sign'] = WeChatHelper.get_sign(params, self.api_key)
        refund_url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
        respone = post(url=refund_url, data=self.convert_request_xml(params), headers={'Content-Type': 'application/xml'}, pkcs12_filename=self.certificate_url, pkcs12_password=self.mch_id)
        response_data = xmltodict.parse(respone.text.encode('ISO-8859-1').decode('utf-8'))['xml']
        if response_data['return_code'] == 'SUCCESS':
            if response_data['result_code'] == 'SUCCESS':
                invoke_result_data.data = response_data['refund_id']
                return invoke_result_data
            else:
                self.logger_error.error("【创建退款单】" + str(response_data))
                invoke_result_data.success = False
                invoke_result_data.error_code="error"
                invoke_result_data.error_message = response_data['err_code_des']
                return invoke_result_data
        else:
            self.logger_error.error("【创建退款单】" + str(response_data))
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = response_data['return_msg']
            return invoke_result_data

    def query_refund(self, refund_no):
        """
        :description: 查询退款单
        :param refund_no：商户退款单号
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if refund_no == "":
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "缺少必填参数refund_no"
            return invoke_result_data
        request_xml = ""
        try:
            params = {
                'appid': self.app_id,
                'mch_id': self.mch_id,
                'nonce_str': WeChatHelper.get_nonce_str(),
                'out_refund_no': str(refund_no),
                'sign_type': 'MD5'
            }
            params['sign'] = WeChatHelper.get_sign(params, self.api_key)
            request_xml = self.convert_request_xml(params)
            queryrefund_url = 'https://api.mch.weixin.qq.com/pay/refundquery'
            respone = requests.post(queryrefund_url, request_xml, headers={'Content-Type': 'application/xml'})
            response_data = xmltodict.parse(respone.text.encode('ISO-8859-1').decode('utf-8'))['xml']
            invoke_result_data.data = response_data
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【查询退款单】" + traceback.format_exc() + ":" + str(request_xml))
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "查询退款单出现异常"
            return invoke_result_data

    def convert_request_xml(self, params):
        """
        :description:拼接XML
        :return: 
        :last_editors: HuangJianYi
        """
        xml = "<xml>"
        for k, v in params.items():
            # v = v.encode('utf8')
            # k = k.encode('utf8')
            xml += '<' + k + '>' + str(v) + '</' + k + '>'
        xml += "</xml>"
        return xml.encode("utf-8")


class WeChatPayReponse(object):
    """
    :description: 微信支付响应类
    """

    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, reponse_xml, api_key=""):
        self.data = WeChatHelper.xml_to_array(reponse_xml)
        pay_config = config.get_value("wechat_pay")
        self.api_key = api_key if api_key else pay_config["api_key"]

    def check_sign(self):
        """
        :description: 校验签名
        :return:
        :last_editors: HuangJianYi
        """
        params = dict(self.data)  # make a copy to save sign
        del params['sign']
        sign = WeChatHelper.get_sign(params, self.api_key)  # 本地签名
        if self.data['sign'] == sign:
            return True
        return False

    def get_data(self):
        """
        :description: 获取微信的通知的数据
        :return:
        :last_editors: HuangJianYi
        """
        return self.data

    def convert_response_xml(self, msg, ok=True):
        """
        :description: 返回xml格式数据
        :return:
        :last_editors: HuangJianYi
        """
        code = "SUCCESS" if ok else "FAIL"
        return WeChatHelper.array_to_xml(dict(return_code=code, return_msg=msg))


class WeChatRefundReponse(object):
    """
    :description: 微信退款响应类
    """
    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, reponse_xml, api_key=""):
        self.data = WeChatHelper.xml_to_array(reponse_xml)
        pay_config = config.get_value("wechat_pay")
        self.api_key = api_key if api_key else pay_config["api_key"]

    def get_data(self):
        """
        :description:获取微信的通知的数据
        :return: 
        :last_editors: HuangJianYi
        """
        return self.data

    def decode_req_info(self, req_info):
        """
        :description:解密退款通知加密参数req_info
        :return: 
        :last_editors: HuangJianYi
        """
        detail_info = CryptoHelper.aes_decrypt(req_info, CryptoHelper.md5_encrypt(self.api_key))
        dict_req_info = xmltodict.parse(detail_info)
        return dict_req_info

    def convert_response_xml(self, msg, ok=True):
        code = "SUCCESS" if ok else "FAIL"
        return WeChatHelper.array_to_xml(dict(return_code=code, return_msg=msg))


class WeChatDataCrypt:
    """
    :description: 微信数据解密帮助类
    """
    def __init__(self, app_id, session_key):
        self.app_id = app_id
        self.session_key = session_key

    def decrypt(self, encryptedData, iv):
        # base64 decode
        session_key = base64.b64decode(self.session_key)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        decrypted = {}
        cipher = AES.new(session_key, AES.MODE_CBC, iv)
        result_data = str(self._unpad(cipher.decrypt(encryptedData)), "utf-8")
        if result_data:
            decrypted = SevenHelper.json_loads(result_data)
        if decrypted:
            if decrypted['watermark']['appid'] != self.app_id:
                raise Exception('Invalid Buffer')
        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]