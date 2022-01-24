# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-01-08 09:56:37
@LastEditTime: 2021-05-01 13:52:16
@LastEditors: HuangJianYi
@Description: 
"""

import hashlib
import json
import optparse
import time
import decimal
from urllib.parse import quote
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
import requests
import xmltodict
from seven_framework.base_model import *
from seven_wxapp.handlers.base.wechat_base import *
from seven_wxapp.handlers.base.seven_helper import *


class WeixinError(Exception):
    def __init__(self, msg):
        super(WeixinError, self).__init__(msg)


class WeiXinPayRequest(object):
    """配置账号信息"""

    # =======【基本信息设置】=====================================
    # 微信公众号身份的唯一标识。审核通过后，在微信发送的邮件中查看
    APPID = ""
    # 受理商ID，身份标识
    MCHID = ""
    # API密钥，需要在商户后台设置
    APIKEY = ""

    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self):

        payconfig = config.get_value("wechat_pay")
        self.APPID = config.get_value("app_id")
        self.APIKEY = payconfig['apikey']
        self.MCHID = payconfig['mchid']

    def get_prepay_id(self, unifiedorder_url, params):
        """
        :description: 获取预支付单号prepay_id
        :param unifiedorder_url：微信下单地址
        :param params：请求参数字典
        :return: 
        :last_editors: HuangJianYi
        """
        redis_key = "wechat_prepay_id:" + str(params['out_trade_no'])
        prepay_id = WeiXinHelper.redis_init().get(redis_key)
        if prepay_id:
            return prepay_id.decode()
        xml = self.get_req_xml(params)
        respone = requests.post(unifiedorder_url, xml, headers={'Content-Type': 'application/xml'})
        msg = respone.text.encode('ISO-8859-1').decode('utf-8')
        #msg = respone.text
        xmlresp = xmltodict.parse(msg)
        if xmlresp['xml']['return_code'] == 'SUCCESS':
            if xmlresp['xml']['result_code'] == 'SUCCESS':
                prepay_id = str(xmlresp['xml']['prepay_id'])
                WeiXinHelper.redis_init().set(redis_key, prepay_id, ex=3600 * 1)
                return prepay_id
            else:
                self.logger_error.error(f"【{params['out_trade_no']},微信统一下单获取prepay_id】" + xmlresp['xml']['err_code_des'])
                return WeixinError(xmlresp['xml']['err_code_des'])
        else:
            self.logger_error.error(f"【{params['out_trade_no']},微信统一下单获取prepay_id】" + xmlresp['xml']['return_msg'])
            return WeixinError(xmlresp['xml']['return_msg'])

    def create_order(self, out_trade_no, body, total_fee, spbill_create_ip, notify_url, open_id="", time_expire="", trade_type="JSAPI"):
        """
        :description: 创建微信预订单
        :param out_trade_no：商户订单号(支付单号)
        :param body：订单描述
        :param total_fee：支付金额
        :param spbill_create_ip：客户端IP
        :param notify_url：微信支付结果异步通知地址
        :param open_id：微信open_id
        :param time_expire：交易结束时间
        :param trade_type：交易类型trade_type为JSAPI时，openid为必填参数！此参数为微信用户在商户对应appid下的唯一标识, 统一支付接口中，缺少必填参数openid！
        :return: 
        :last_editors: HuangJianYi
        """
        spbill_create_ip = spbill_create_ip if SevenHelper.is_ip(spbill_create_ip) == True else "127.0.0.1"

        params = {
            'appid': self.APPID,  # appid
            'mch_id': self.MCHID,  # 商户号
            'nonce_str': self.get_nonceStr(),
            'body': body,
            'out_trade_no': str(out_trade_no),
            'total_fee': str(int(decimal.Decimal(str(total_fee)) * 100)),
            'spbill_create_ip': spbill_create_ip,
            'trade_type': trade_type,
            'notify_url': notify_url
        }
        if trade_type == "JSAPI":
            if open_id == "":
                return WeixinError("缺少必填参数open_id")
            else:
                params['openid'] = open_id
        if time_expire != "":
            params['time_expire'] = str(time_expire)

        # 开发者调用支付统一下单API生成预交易单
        unifiedorder_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        prepay_id = self.get_prepay_id(unifiedorder_url, params)
        if type(prepay_id) == WeixinError:
            return prepay_id

        params['prepay_id'] = prepay_id
        params['package'] = f"prepay_id={prepay_id}"
        params['timestamp'] = str(int(time.time()))
        sign_again_params = {'appId': params['appid'], 'nonceStr': params['nonce_str'], 'package': params['package'], 'signType': 'MD5', 'timeStamp': params['timestamp']}
        return self.get_sign(sign_again_params)  # 返回给app

    def query_order(self, out_trade_no="", transaction_id=""):
        """
        :description: 查询订单
        :param transaction_id：微信订单号
        :param out_trade_no：商户订单号(支付单号)
        :return: 
        :last_editors: HuangJianYi
        """
        if transaction_id == "" and out_trade_no == "":
            return WeixinError("缺少必填参数transaction_id或out_trade_no")
        xmlresp = {}
        xml = ""
        try:
            params = {
                'appid': self.APPID,  # appid
                'mch_id': self.MCHID,  # 商户号
                'nonce_str': self.get_nonceStr(),
            }
            if transaction_id != "":
                params['transaction_id'] = str(transaction_id)  # 微信交易单号
            if out_trade_no != "":
                params['out_trade_no'] = str(out_trade_no)  # 支付单号

            xml = self.get_req_xml(params)
            queryorder_url = 'https://api.mch.weixin.qq.com/pay/orderquery'  # 微信请求url
            respone = requests.post(queryorder_url, xml, headers={'Content-Type': 'application/xml'})
            msg = respone.text.encode('ISO-8859-1').decode('utf-8')
            xmlresp = xmltodict.parse(msg)
        except Exception as ex:
            self.logger_error.error(f"【微信查询订单】" + str(ex) + ":" + str(xml))
            return WeixinError("微信查询订单出现异常")
        return xmlresp

    def close_order(self, out_trade_no=""):
        """
        :description: 关闭订单
        :param out_trade_no：商户订单号(支付单号)
        :return: 
        :last_editors: HuangJianYi
        """
        if out_trade_no == "":
            return WeixinError("缺少必填参数out_trade_no")
        xmlresp = {}
        try:
            params = {
                'appid': self.APPID,  # appid
                'mch_id': self.MCHID,  # 商户号
                'nonce_str': self.get_nonceStr(),
                'out_trade_no': str(out_trade_no)  # 支付单号
            }
            xml = self.get_req_xml(params)
            queryorder_url = 'https://api.mch.weixin.qq.com/pay/closeorder'  # 微信请求url
            respone = requests.post(queryorder_url, xml, headers={'Content-Type': 'application/xml'})
            msg = respone.text.encode('ISO-8859-1').decode('utf-8')
            xmlresp = xmltodict.parse(msg)
        except Exception as ex:
            self.logger_error.error(f"【微信关闭订单】" + str(ex))
            return WeixinError("微信关闭订单出现异常")
        return xmlresp

    def get_pay_status(self, out_trade_no, transaction_id=""):
        """
        :description: 查询订单状态
        :param transaction_id：微信订单号
        :return: 
        :last_editors: HuangJianYi
        """
        xmlresp = self.query_order(out_trade_no, transaction_id)
        if type(xmlresp) == WeixinError:
            return ""
        else:
            if xmlresp['xml']['return_code'] == 'SUCCESS':
                if xmlresp['xml']['result_code'] == 'SUCCESS':
                    return str(xmlresp['xml']['trade_state'] if xmlresp['xml'].__contains__("trade_state") else "")  # SUCCESS--支付成功REFUND--转入退款NOTPAY--未支付CLOSED--已关闭REVOKED--已撤销(刷卡支付)USERPAYING--用户支付中PAYERROR--支付失败(其他原因，如银行返回失败)ACCEPT--已接收，等待扣款
                else:
                    return ""
            else:
                return ""

    def get_nonceStr(self, length=32):
        """生成随机字符串"""
        import random
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)

    def key_value_url(self, value, urlencode):
        """
        将键值对转为 key1=value1&key2=value2
        对参数按照key=value的格式，并按照参数名ASCII字典序排序
        """
        slist = sorted(value)
        buff = []
        for k in slist:
            v = quote(value[k]) if urlencode else value[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    def get_sign(self, params):
        """
        生成sign
        拼接API密钥
        """
        stringA = self.key_value_url(params, False)
        stringSignTemp = stringA + '&key=' + self.APIKEY  # APIKEY, API密钥，需要在商户后台设置
        sign = (hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()).upper()
        params['sign'] = sign
        return params

    def get_req_xml(self, params):
        """
        拼接XML
        """
        params = self.get_sign(params)
        xml = "<xml>"
        for k, v in params.items():
            # v = v.encode('utf8')
            # k = k.encode('utf8')
            xml += '<' + k + '>' + v + '</' + k + '>'
        xml += "</xml>"
        return xml.encode("utf-8")


class WeiXinPayReponse(object):
    SUCCESS, FAIL = "SUCCESS", "FAIL"
    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, xml):
        payconfig = config.get_value("wechat_pay")
        self.xml = xml
        self.data = self.xml_to_array(xml)  # 接收到的数据，类型为关联数组
        self.APIKEY = payconfig['apikey']

    def format_bizquery_paramap(self, paraMap, urlencode):
        """格式化参数，签名过程需要使用"""
        slist = sorted(paraMap)
        buff = []
        for k in slist:
            v = quote(paraMap[k]) if urlencode else paraMap[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    def get_sign(self, obj):
        """生成签名"""
        # 签名步骤一：按字典序排序参数,format_bizquery_paramap已做
        String = self.format_bizquery_paramap(obj, False)
        # 签名步骤二：在string后加入KEY
        String = "{0}&key={1}".format(String, self.APIKEY)
        # 签名步骤三：MD5加密
        # String = hashlib.md5(String).hexdigest()
        String = hashlib.md5(String.encode("utf-8")).hexdigest()
        # 签名步骤四：所有字符转为大写
        result_ = String.upper()
        return result_

    def xml_to_array(self, xml):
        """将xml转为array"""
        array_data = {}
        # root = ET.fromstring(self.xml)
        root = ElementTree.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data

    def array_to_xml(self, arr):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in arr.items():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    def check_sign(self):
        """校验签名"""
        tmpData = dict(self.data)  # make a copy to save sign
        del tmpData['sign']
        sign = self.get_sign(tmpData)  # 本地签名
        if self.data['sign'] == sign:
            return True
        return False

    def get_data(self):
        """获取微信的通知的数据"""
        return self.data

    def get_return_data(self, msg, ok=True):
        code = "SUCCESS" if ok else "FAIL"
        return self.array_to_xml(dict(return_code=code, return_msg=msg))


class WeiXinRefundReponse(object):

    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, xml):
        payconfig = config.get_value("wechat_pay")
        self.xml = xml
        self.data = xmltodict.parse(xml)  # 接收到的数据
        self.APIKEY = payconfig['apikey']

    def array_to_xml(self, arr):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in arr.items():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    def get_data(self):
        """获取微信的通知的数据"""
        return self.data

    def decode_req_info(self, req_info):
        """解密退款通知加密参数req_info"""
        detail_info = CryptoHelper.aes_decrypt(req_info, CryptoHelper.md5_encrypt(self.APIKEY))
        dict_req_info = xmltodict.parse(detail_info)
        return dict_req_info

    def get_return_data(self, msg, ok=True):
        code = "SUCCESS" if ok else "FAIL"
        return self.array_to_xml(dict(return_code=code, return_msg=msg))