# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-01-14 10:44:07
@LastEditTime: 2022-01-10 13:54:31
@LastEditors: HuangJianYi
@Description: 
"""
import requests
import json
import hashlib
from Crypto.Cipher import AES
import base64
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_framework.base_model import *
from seven_cloudapp_frame.models.seven_model import InvokeResultData


class TikTokHelper:
    """
    :description: 抖音帮助类 1.临时登录凭证校验获取open_id、session_key  2.解析加密数据
    """
    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def code2_session(self, code="", anonymous_code="", app_id="", app_secret=""):
        """
        :description:获取open_id、session_key等信息
        :param code: 登录票据,非匿名需要 code
        :param anonymous_code: 非匿名下的 anonymous_code 用于数据同步，匿名需要 anonymous_code
        :param app_id: app_id
        :param app_secret: app_secret
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")
        app_secret = app_secret if app_secret else config.get_value("app_secret")

        invoke_result_data = InvokeResultData()
        redis_key = f"{app_id}_tiktok_login_code:{code}"
        redis_init = SevenHelper.redis_init()
        code2_session_dict = redis_init.get(redis_key)
        if code2_session_dict:
            code2_session_dict = SevenHelper.json_loads(code2_session_dict)
            invoke_result_data.data = code2_session_dict
            return invoke_result_data
        param = {
            'code': code,  # 用户点击按钮跳转到抖音授权页, 抖音处理完后重定向到redirect_uri, 并给我们加上code=xxx的参数, 这个code就是我们需要的
            'appid': app_id,
            'secret': app_secret,
            'anonymous_code': anonymous_code,
        }
        response = None
        try:
            requset_url = 'https://developer.toutiao.com/api/apps/v2/jscode2session'
            headers = {"Content-type": "application/json"}
            response = requests.post(requset_url, headers=headers, data=json.dumps(param))
            response_data = SevenHelper.json_loads(response.text)
            if response_data.__contains__("err_no") and response_data["err_no"] != 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = response_data["err_no"]
                invoke_result_data.error_message = response_data["err_tips"]
                return invoke_result_data
            open_id = response_data["data"]['openid']
            session_key = response_data["data"]['session_key']
            redis_init.set(redis_key, SevenHelper.json_dumps(response_data["data"]), ex=60 * 60)
            redis_init.set(f"{app_id}_tiktok_sessionkey:{str(open_id)}", session_key, ex=60 * 60)
            invoke_result_data.data = response_data["data"]
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【code2_session】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = traceback.format_exc()
            return invoke_result_data

    @classmethod
    def get_access_token(self, grant_type="client_credential", app_id="", app_secret=""):
        """
        :description:access_token 是小程序的全局唯一调用凭据，开发者调用小程序支付时需要使用 access_token。access_token 的有效期为 2 个小时，需要定时刷新 access_token，重复获取会导致之前一次获取的 access_token 的有效期缩短为 5 分钟。
        :param grant_type: 获取access_token 时值为 client_credential
        :param app_id: app_id
        :param app_secret: app_secret
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
        redis_key = f"tiktok_access_token:{str(app_id)}"
        try:
            access_token = redis_init.get(redis_key)
            if access_token:
                invoke_result_data.data = access_token
                return invoke_result_data
            requset_url = 'https://developer.toutiao.com/api/apps/token'
            headers = {"Content-type": "application/json"}
            response = requests.post(requset_url, headers=headers, data=json.dumps(param))
            response_data = SevenHelper.json_loads(response.text)
            if response_data.__contains__("err_no") and response_data["err_no"] != 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = response_data["err_no"]
                invoke_result_data.error_message = response_data["err_tips"]
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
    def decrypt_data_by_code(self, open_id, code, encrypted_Data, iv, app_id="", app_secret=""):
        """
        :description:解析加密数据，客户端判断是否登录状态，如果登录只传open_id不传code，如果是登录过期,要传code重新获取session_key
        :param open_id：open_id
        :param code：登录票据
        :param encrypted_Data：加密数据,抖音返回加密参数
        :param iv：抖音返回参数
        :param app_id: app_id
        :param app_secret: app_secret
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")
        app_secret = app_secret if app_secret else config.get_value("app_secret")

        data = {}
        if code:
            code2_session_dict = self.code2_session(code=code, app_id=app_id, app_secret=app_secret)
            if code2_session_dict:
                open_id = code2_session_dict["openid"]
        try:
            session_key = SevenHelper.redis_init().get(f"{app_id}_tiktok_sessionkey:{str(open_id)}")
            data_crypt = TikTokBizDataCrypt(app_id, session_key)
            data = data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error("【decrypt_data_by_code】" + traceback.format_exc())
        return data

    @classmethod
    def decrypt_data(self, session_key, encrypted_Data, iv, app_id=""):
        """
        :description:解析加密数据
        :param session_key: session_key调用登录接口获得
        :param encrypted_Data：加密数据,抖音返回加密参数
        :param iv：抖音返回参数
        :param app_id: 抖音小程序标识
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        app_id = app_id if app_id else config.get_value("app_id")

        data = {}
        try:
            data_crypt = TikTokBizDataCrypt(app_id, session_key)
            #data中是解密的信息
            data = data_crypt.decrypt(encrypted_Data, iv)
        except Exception as ex:
            self.logger_error.error("【decrypt_data】" + traceback.format_exc())
        return data

    @classmethod
    def create_qr_code(self, access_token, appname="douyin", path="", width=430, line_color={ "r": 0, "g": 0, "b": 0 }, background={ "r": 255, "g": 255, "b": 255 }):
        """
        :description:获取小程序/小游戏的二维码。该二维码可通过任意 app 扫码打开，能跳转到开发者指定的对应字节系 app 内拉起小程序/小游戏， 并传入开发者指定的参数。通过该接口生成的二维码，永久有效，暂无数量限制。
        :param access_token: 服务端 API 调用标识
        :param appname: 打开二维码的字节系 app 名称
        :param path: 小程序/小游戏启动参数，小程序则格式为 encode({path}?{query})，小游戏则格式为 JSON 字符串，默认为空
        :param width: 二维码宽度，单位 px，最小 280px，最大 1280px，默认为 430px
        :param line_color: 二维码线条颜色，默认为黑色
        :param background: 二维码背景颜色，默认为白色
        :return: 图片二进制 数据类型Array<byte>
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        param = {
                "appname": appname,
                "access_token": access_token,
                "path": path,
                "width": width,
                "line_color": line_color,
                "background": background
                }
        response = ""
        try:
            requset_url = 'https://developer.toutiao.com/api/apps/token'
            headers = {"Content-type": "application/json"}
            response = requests.post(requset_url, headers=headers, data=json.dumps(param))
            response_data = SevenHelper.json_loads(response.text)
            if response_data["errcode"] != 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = response_data["err_no"]
                invoke_result_data.error_message = response_data["err_tips"]
                return invoke_result_data
            return response_data
        except Exception as ex:
            self.logger_error.error("【create_qr_code】" + traceback.format_exc() + ":" + str(response.text))
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = traceback.format_exc()
            return invoke_result_data


class TikTokPayRequest(object):
    """
    :description: 抖音支付请求类,配置文件内容 "tiktok_pay": {"cp_extra": "","token": "","salt": ""}
    """
    # =======【基本信息设置】=====================================
    # 抖音公众号身份的唯一标识。审核通过后，在抖音发送的邮件中查看
    app_id = ""
    #开发者自定义字段，回调原样回传
    cp_extra = ""
    #担保交易Token（令牌）
    token = ""
    #担保交易密钥
    salt = ""
    # 日志
    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, app_id="", cp_extra="", token="", salt=""):
        """
        :description: 初始化
        :last_editors: HuangJianYi
        """
        pay_config = config.get_value("tiktok_pay")
        self.app_id = app_id if app_id else config.get_value("app_id")
        self.cp_extra = cp_extra if cp_extra else pay_config["cp_extra"]
        self.token = token if token else pay_config["token"]
        self.salt = salt if salt else pay_config["salt"]

    def create_order(self, pay_order_no, notify_url, total_amount=1, subject="", body="", valid_time=900, thirdparty_id="", disable_msg=None, msg_page=""):
        """
        :description: 服务端创建预下单
        :param pay_order_no：商户订单号(支付单号)开发者服务端的唯一订单号
        :param notify_url：支付结果异步通知地址
        :param total_amount:支付价格;单位元
        :param subject: 商品描述; 长度限制 128 字节，不超过 42 个汉字 |默认 自己约定一个比如 “福小宠商品”*|
        :param body:商品详情|默认 自己约定一个比如 “福小宠商品”
        :param valid_time:订单过期时间(秒); 最小 15 分钟，最大两天|默认 900
        :param thirdparty_id:服务商模式接入必传,第三方平台服务商 id，非服务商模式留空|默认传空字符串
        :param disable_msg:是否屏蔽担保支付的推送消息，1-屏蔽 0-非屏蔽，接入 POI 必传|默认传None
        :param msg_page:担保支付消息跳转页|默认传空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            data = {}
            data['app_id'] = self.app_id
            data['out_order_no'] = pay_order_no
            data['total_amount'] = int(decimal.Decimal(str(total_amount)) * 100)
            data['subject'] = subject
            data['body'] = body
            data['valid_time'] = valid_time
            if notify_url:
                data['notify_url'] = notify_url
            if self.cp_extra:
                data['cp_extra'] = self.cp_extra
            if disable_msg:
                data['disable_msg'] = int(disable_msg)
            if msg_page:
                data['msg_page'] = msg_page
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            sign = self.get_sign(data)
            # 如果有第三方平台服务商id:thirdparty_id字段请把他放入data的字典里面
            data['sign'] = sign

            redis_key = f"{self.app_id}_tiktok_order_id:{str(pay_order_no)}"
            orderInfo = SevenHelper.redis_init().get(redis_key)
            if orderInfo:
                invoke_result_data.data = SevenHelper.json_loads(orderInfo)
                return invoke_result_data

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/create_order"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = SevenHelper.json_loads(response.text)
            # err_no	number	    状态码 0-业务处理成功
            # err_tips	string	    错误提示信息，常见错误处理可参考附录常见问题章节
            # data	    orderInfo	拉起收银台的 orderInfo
            # {"err_no": 2000, "err_tips": "单号记录不存在", "data": null}
            if response_data['err_no'] == 0:
                SevenHelper.redis_init().set(redis_key, SevenHelper.json_dumps(response_data['data']), ex=3600 * 1)
                invoke_result_data.data = response_data['data']
                return invoke_result_data
            else:
                self.logger_error.error(f"【{pay_order_no},创建预下单】" + response_data['err_tips'])
                invoke_result_data.success = False
                invoke_result_data.error_code="error"
                invoke_result_data.error_message = response_data['err_tips']
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【创建预下单】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "创建预下单出现异常，请重试"
            return invoke_result_data

    def query_order(self, pay_order_no, thirdparty_id=""):
        """
        :description: 查询订单
        :param pay_order_no：开发者侧的订单号, 不可重复
        :param thirdparty_id: 服务商模式接入必传  第三方平台服务商 id，非服务商模式留空字符串|默认值 空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            data = {}
            data['out_order_no'] = pay_order_no
            sign = self.get_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/query_order"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = SevenHelper.json_loads(response.text)
            # {"err_no": 2000, "err_tips": "单号记录不存在", "out_order_no": "", "order_id": "", "payment_info": null}
            # payment_info 返回值结构如下：
            # {
            #     "total_fee": 1200,
            #     "order_status": "PROCESSING-处理中|SUCCESS-成功|FAIL-失败|TIMEOUT-超时",
            #     "pay_time": "支付时间",
            #     "way": 1,
            #     "channel_no": "渠道单号",
            #     "channel_gateway_no": "渠道网关号"
            # }
            if response_data['err_no'] == 0:
                invoke_result_data.data = response_data
                return invoke_result_data
            else:
                self.logger_error.error(f"【{pay_order_no},查询订单】" + response_data['err_tips'])
                invoke_result_data.success = False
                invoke_result_data.error_code="error"
                invoke_result_data.error_message = response_data['err_tips']
                return invoke_result_data

        except Exception as ex:
            self.logger_error.error("【查询订单】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "查询订单出现异常，请重试"
            return invoke_result_data

    def get_pay_status(self, pay_order_no, thirdparty_id=""):
        """
        :description: 查询订单状态
        :param pay_order_no：开发者侧的订单号, 不可重复
        :param thirdparty_id: 服务商模式接入必传  第三方平台服务商 id，非服务商模式留空字符串|默认值 空字符串
        :return: PROCESSING-处理中|SUCCESS-成功|FAIL-失败|TIMEOUT-超时
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data = self.query_order(pay_order_no, thirdparty_id)
        if invoke_result_data.success == False:
            return ""
        else:
            response_data = invoke_result_data.data
            if response_data['payment_info']:
                return response_data['payment_info']['order_status']
            else:
                return ""

    def create_refund(self, refund_no, pay_order_no, notify_url, refund_amount=1, reason="", thirdparty_id="", disable_msg=None, msg_page="", all_settle=None):
        """
        :description: 服务端退款请求
        :param refund_no:开发者侧的退款单号, 不可重复
        :param pay_order_no:商户分配订单号，标识进行退款的订单，开发者服务端的唯一订单号
        :param notify_url:退款通知地址
        :param refund_amount: 退款金额；单位元
        :param reason:退款理由，长度上限 100|默认 由开发者定 例如：“7天无理由退款”
        :param thirdparty_id:服务商模式接入必传,第三方平台服务商 id，非服务商模式留空|默认传空字符串
        :param disable_msg:是否屏蔽担保支付的推送消息，1-屏蔽 0-非屏蔽，接入 POI 必传|默认传None
        :param msg_page:担保支付消息跳转页|默认传空字符串
        :param all_settle:是否为分账后退款，1-分账后退款；0-分账前退款。分账后退款会扣减可提现金额，请保证余额充足*|默认传None
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            data = {}
            data['app_id'] = self.app_id
            data['out_refund_no'] = refund_no
            data['out_order_no'] = pay_order_no
            data['refund_amount'] = int(decimal.Decimal(str(refund_amount)) * 100)
            data['reason'] = reason
            #cp_extra 开发者自定义字段，回调原样回传
            if self.cp_extra:
                data['cp_extra'] = self.cp_extra
            if notify_url:
                data['notify_url'] = notify_url
            if disable_msg:
                data['disable_msg'] = int(disable_msg)
            if msg_page:
                data['msg_page'] = msg_page
            if all_settle:
                data['all_settle'] = int(all_settle)
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            sign = self.get_sign(data)
            # 如果有第三方平台服务商 id :thirdparty_id字段请把他放入data.update的字典里面
            data['sign'] = sign

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/create_refund"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = SevenHelper.json_loads(response.text)
            if response_data['err_no'] == 0:
                invoke_result_data.data = response_data
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【创建退款单】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "退款出现异常，请重试"
            return invoke_result_data

    def query_refund(self, refund_no="", thirdparty_id=""):
        """
        :desciption:退款查询
        :param refund_no:开发者侧的退款单号, 不可重复
        :param thirdparty_id:服务商模式接入必传  第三方平台服务商 id，非服务商模式留空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            data = {}
            data['out_refund_no'] = refund_no
            sign = self.get_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/query_refund"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = SevenHelper.json_loads(response.text)
            if response_data['err_no'] == 0:
                invoke_result_data.data = response_data
                return invoke_result_data

        except Exception as ex:
            self.logger_error.error("【退款查询】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "退款查询出现异常，请重试"
            return invoke_result_data

    def create_settle(self, pay_order_no="", settle_desc="", settle_params="", thirdparty_id=""):
        """
        :description:服务端结算请求
        :param order_no:商户分配订单号，标识进行退款的订单，开发者服务端的唯一订单号
        :param settle_desc:结算描述 默认 自己约定一个比如 “福小宠商品结算”
        :param settle_params:其他分账方信息，分账分配参数 SettleParameter 数组序列化后生成的 json 格式字符串
        :param thirdparty_id：服务商模式接入必传,第三方平台服务商 id，非服务商模式留空|默认传空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            #out_order_no 开发者服务端的唯一订单号
            out_settle_no = SevenHelper.create_order_id()
            #回调地址
            notify_url = self.notify_url
            cp_extra = self.cp_extra
            # 在这里将分账信息存入数据库
            data = {}
            data['out_settle_no'] = out_settle_no
            #cp_extra 开发者自定义字段，回调原样回传
            data['cp_extra'] = cp_extra
            data['notify_url'] = notify_url
            data['out_order_no'] = pay_order_no
            data['settle_desc'] = settle_desc
            if settle_params:
                data['settle_params'] = settle_params
            sign = self.get_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/settle"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = SevenHelper.json_loads(response.text)
            if response_data['err_no'] == 0:
                invoke_result_data.data = response_data
                return invoke_result_data

        except Exception as ex:
            self.logger_error.error("【结算请求】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "结算请求出现异常，请重试"
            return invoke_result_data

    def query_settle(self, out_settle_no="", thirdparty_id=""):
        """
        :desciption:结算查询
        :param out_settle_no:开发者侧的分账号, 不可重复
        :param thirdparty_id:服务商模式接入必传  第三方平台服务商 id，非服务商模式留空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            data = {}
            data['out_settle_no'] = out_settle_no
            sign = self.get_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/query_settle"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = SevenHelper.json_loads(response.text)
            if response_data['err_no'] == 0:
                invoke_result_data.data = response_data
                return invoke_result_data

        except Exception as ex:
            self.logger_error.error("【结算查询】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "结算查询出现异常，请重试"
            return invoke_result_data

    def get_sign(self, params_map):
        params_list = []
        for k, v in params_map.items():
            if k == "other_settle_params":
                continue
            value = str(v).strip()
            if value.startswith("\"") and value.endswith("\"") and len(value) > 1:
                value = value[1: len(value) - 1]
            value = value.strip()
            if value == "" or value == "null":
                continue
            if k not in ("app_id", "thirdparty_id", "sign"):
                params_list.append(value)
        params_list.append(self.salt)
        params_list.sort()
        original_str = str("&").join(params_list)
        return hashlib.md5(original_str.encode("utf-8")).hexdigest()


class TikTokReponse(object):
    """
    :description: 抖音支付响应类 根据支付/退款/分账等回调json内容，检测type字段判断是支付回调还是退款回调，type:payment 支付成功回调,refund退款成功回调,settle分账成功回调
    """
    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, data, token=""):
        self.data = json.loads(data)  #data由json.loads(self.request.body)获得
        pay_config = config.get_value("tiktok_pay")
        self.token = token if token else pay_config["token"]

    def get_data(self):
        """
        :description: 获取通知的数据
        :return:
        :last_editors: HuangJianYi
        """
        return self.data

    def check_sign(self):
        """
        :description: 校验签名
        :return:
        :last_editors: HuangJianYi
        """
        #计算服务端sign
        service_signature = self.get_callback_sign(self.data)
        #验证成功,进行业务处理
        log_msg = f'客户端签名:{self.data["msg_signature"]},服务端签名:{service_signature}'
        # self.logger_error.error(log_msg)
        if service_signature == self.data["msg_signature"]:
            return True
        else:
            return False

    def get_callback_sign(self, params):
        """
        :description: 获取头条回调sign
        :param params: 参数字典
        :return: sign
        :last_editors: HuangJianYi
        """
        keys = ['type', 'msg_signature']
        params_copy = {key: params[key] for key in params if key not in keys}
        for key, v in params_copy.items():
            value = str(v).strip()
            if value.startswith("\"") and value.endswith("\"") and len(value) > 1:
                value = value[1:len(value) - 1]
            value = value.strip()
            if value == "" or value == "null":
                continue
            if isinstance(value, int):
                params_copy[key] = str(value)
        params_copy['token'] = self.token
        params_list = sorted(list(params_copy.items()), key=lambda x: x[1])
        params_str = ''.join(f"{v}" for k, v in params_list)
        sign = CryptoHelper().sha1_encrypt(params_str)
        return sign

    def convert_response_json(self, err_no=0, err_tips="success"):
        """
        :description: 获取通知的数据
        :return:
        :last_editors: HuangJianYi
        """
        return {"err_no": err_no, "err_tips": err_tips}


class TikTokBizDataCrypt:
    def __init__(self, app_id, session_key):
        self.app_id = app_id
        self.session_key = session_key

    def decrypt(self, encryptedData, iv):
        """
        :description: 解密
        :param encryptedData: encryptedData
        :param iv: iv
        :return str
        :last_editors: HuangJianYi
        """
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
