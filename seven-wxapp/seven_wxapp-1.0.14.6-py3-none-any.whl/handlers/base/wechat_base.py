# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-01-14 10:44:07
@LastEditTime: 2021-05-06 10:53:52
@LastEditors: HuangJianYi
@Description: 
"""
import requests
import json
from Crypto.Cipher import AES
import base64
from seven_framework.base_model import *
from seven_framework.redis import *


class WeiXinHelper:

    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def get_open_id(self, code, grant_type="authorization_code"):
        """
        :description:获取 openid
        :param code：登录票据
        :param grant_type：授权方式
        :return: 
        :last_editors: HuangJianYi
        """
        redis_key = "wechat_login_code:" + str(code)
        open_id = self.redis_init().get(redis_key)
        if open_id:
            return open_id.decode()

        app_id = config.get_value("app_id")
        app_secret = config.get_value("app_secret")
        param = {
            'js_code': code,  # 用户点击按钮跳转到微信授权页, 微信处理完后重定向到redirect_uri, 并给我们加上code=xxx的参数, 这个code就是我们需要的
            'appid': app_id,
            'secret': app_secret,
            'grant_type': grant_type,
        }

        # 通过code获取access_token
        openIdUrl = 'https://api.weixin.qq.com/sns/jscode2session'
        resp = None
        try:
            resp = requests.get(openIdUrl, params=param)
            res_result = json.loads(resp.text)
            open_id = res_result['openid']
            session_key = res_result['session_key']
            self.redis_init().set(redis_key, open_id, ex=10 * 1)
            self.redis_init().set(f"sessionkey:{str(open_id)}", session_key, ex=60 * 60)
            return open_id
            # return resp.text
        except Exception as ex:
            self.logger_error.error(str(ex) + "【微信get_open_id】" + str(resp.text))
            return ""
        return ""

    @classmethod
    def decrypted_data(self, open_id, code, encrypted_Data, iv):
        """
        :description:解析加密数据，客户端判断是否登录状态，如果登录只传open_id不传code，如果是登录过期,要传code重新获取session_key
        :param open_id：open_id
        :param code：登录票据
        :param encrypted_Data：加密数据,微信返回加密参数
        :param iv：微信返回参数
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        app_id = config.get_value("app_id")
        data = {}
        if code:
            open_id = self.get_open_id(code)
        try:
            session_key = self.redis_init().get(f"sessionkey:{str(open_id)}")
            if session_key:
                session_key = session_key.decode()
            wx_data_crypt = WXBizDataCrypt(app_id, session_key)
            data = wx_data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error(str(ex) + "【微信decrypted_data】")

        return data

    @classmethod
    def decrypt_data(self, app_id, session_key, encrypted_Data, iv):
        """
        :description:解析加密数据
        :param app_id: 微信小程序标识
        :param session_key: session_key调用登录接口获得
        :param encrypted_Data：加密数据,微信返回加密参数
        :param iv：微信返回参数
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        data = {}
        try:
            wx_data_crypt = WXBizDataCrypt(app_id, session_key)
            data = wx_data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error(str(ex) + "【微信decrypted_data】")
        return data

    @classmethod
    def redis_init(self, db=None, decode_responses=False):
        """
        :description: redis初始化
        :return: redis_cli
        :last_editors: HuangJianYi
        """
        host = config.get_value("redis")["host"]
        port = config.get_value("redis")["port"]
        if not db:
            db = config.get_value("redis")["db"]
        password = config.get_value("redis")["password"]
        redis_cli = RedisHelper.redis_init(host, port, db, password, decode_responses)
        return redis_cli


class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        decrypted = {}
        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        result_data = str(self._unpad(cipher.decrypt(encryptedData)), "utf-8")
        if result_data:
            decrypted = json.loads(result_data)
        if decrypted:
            if decrypted['watermark']['appid'] != self.appId:
                raise Exception('Invalid Buffer')
        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]
