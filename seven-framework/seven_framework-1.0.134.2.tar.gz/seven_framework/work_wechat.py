# -*-coding:utf-8-*-
"""
:Author: LinGuilin
:Date: 2020-08-21 14:07:08
:LastEditTime: 2020-08-26 17:06:34
:LastEditors: LinGuilin
:Description: 企业微信应用接口调用

"""

from seven_framework.sign import SignHelper
import time
import requests
import traceback


class WorkWechatHelper(object):
    """"
    :Description:企业微信应用接口类
    Usage::

      >>> from seven_framework import *
      >>> work_wechat = WorkWechatHelper(app_id=APP_ID,app_key=APP_KEY)
      >>> res = work_wechat.get_web_auth_link(redirect_uri='https://httpbin.org/get',state=STATE)
      >>> if res:
      >>>       print('res)
      https://open.weixin.qq.com/connect/oauth2/...
    """
    def __init__(self, app_id, app_key, oauth_url=None, msg_url=None):
        """
        :Description: 初始化参数
        :param app_id: 应用id
        :param app_key: 应用凭证
        :param oauth_url: 登录认证请求路径
        :param msg_url: 消息请求路径
        :last_editors: LinGuilin
        """
        self.oauth_url = oauth_url
        self.msg_url = msg_url

        if not oauth_url:
            self.oauth_url = "https://wwc.gao7.com/api/auth/get_link"

        if not msg_url:
            self.msg_url = "https://wwc.gao7.com/api/message/send"

        self.app_key = app_key
        self.app_id = app_id

    def _get_oauth_params(self, redirect_uri, link_type, state=None):
        """
        :Description: 获取登录认证请求参数字典
        :param redirect_uri:重定向链接
        :param state: 透传参数
        :param link_type: 链接类型 code/web
        :return dict  请求参数字典 
        :last_editors: LinGuilin
        """

        timestamp = int(time.time())
        params = {}
        params["timestamp"] = timestamp
        params["redirect_uri"] = redirect_uri
        params["state"] = state
        params["link_type"] = link_type
        params["app_id"] = self.app_id

        # 生成签名
        sign = SignHelper.params_sign_md5(params=params, app_key=self.app_key)
        # 构造请求参数
        params["sign"] = sign
        return params

    def _get_msg_params(self,
                        notice_content,
                        notice_object,
                        notice_object_type,
                        notice_content_type="text",
                        webhook_key=None):
        """
        :Description: 获取消息请求参数
        :param notice_content: 消息内容
        :param notice_content_type: 消息内容类型
        :param notice_object: 消息接收对象
        :param notice_object_type: 消息接收对象类型
        :param webhook_key:机器人密钥
        :return dict  消息字典
        :last_editors: LinGuilin
        """

        timestamp = int(time.time())
        params = {}
        params["app_id"] = self.app_id
        params["timestamp"] = timestamp
        params["notice_object_type"] = notice_object_type
        params["notice_content"] = notice_content
        params["notice_content_type"] = notice_content_type
        params["notice_object"] = notice_object
        params["webhook_key"] = webhook_key
        # 生成签名
        sign = SignHelper.params_sign_md5(params=params, app_key=self.app_key)

        # 构建请求字典
        params["sign"] = sign
        return params

    def get_web_auth_link(self, redirect_uri, state=None):
        """
        :Description: 获取网页认证登录链接
        :param redirect_uri: 重定向链接 
        :param state: 透传参数
        :return 链接或者None
        :last_editors: LinGuilin
        """

        params = self._get_oauth_params(redirect_uri=redirect_uri,
                                        state=state,
                                        link_type="web")
        try:
            response = requests.get(url=self.oauth_url, params=params)
            response.raise_for_status()
            res = response.json()

        except:
            print(f"get请求url:{self.oauth_url},params:{params} 异常:{traceback.format_exc()}")
            return None
        else:
            if int(res["result"]) == 1:
                return res["data"]["auth_url"]
            print(f"get请求url:{self.oauth_url}出现异常,异常信息:{res['desc']}")
            return None

    def get_code_auth_link(self, redirect_uri, state=None):
        """
        :Description: 获取二维码认证登录链接
        :param redirect_uri: 重定向链接 
        :param state: 透传参数
        :return 链接或者None
        :last_editors: LinGuilin
        """

        params = self._get_oauth_params(redirect_uri=redirect_uri,
                                        state=state,
                                        link_type="code")

        try:
            response = requests.get(url=self.oauth_url, params=params)
            response.raise_for_status()
            res = response.json()
        except:
            print(f"get请求url:{self.oauth_url},params:{params} 异常:{traceback.format_exc()}")
            return None
        else:

            if int(res["result"]) == 1:
                return res["data"]["auth_url"]
            print(f"get请求url:{self.oauth_url}出现异常,异常信息:{res['desc']}")
            return None

    def send_msg_by_webhook(self,
                            notice_content,
                            notice_object,
                            webhook_key,
                            notice_content_type="text"):
        """
        :Description: 发送机器人消息
        :param notice_content: 消息内容
        :param notice_content_type: 消息内容类型
        :param notice_object: 消息接收对象
        :param webhook_key: 机器人密钥
        :return 成功为True 失败 None
        :last_editors: LinGuilin
        """

        params = self._get_msg_params(notice_content=notice_content,
                                      notice_content_type=notice_content_type,
                                      notice_object=notice_object,
                                      webhook_key=webhook_key,
                                      notice_object_type="webhook")

        try:
            response = requests.post(
                url=self.msg_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            response.raise_for_status()
            res = response.json()

        except:
            print(f"post请求url:{self.msg_url},params:{params} 异常:{traceback.format_exc()}")
            return None
        else:

            if int(res["result"]) == 1:
                return True
            print(f"post请求url:{self.msg_url}出现异常,异常信息:{res['desc']}")
            return None

    def send_msg_by_template(self,
                             notice_content,
                             notice_object,
                             notice_content_type="text"):
        """
        :Description: 发送模板消息
        :param notice_content: 消息内容
        :param notice_content_type: 消息内容类型
        :param notice_object: 消息接收对象
        :return 成功为True 失败 None
        :last_editors: LinGuilin
        """

        params = self._get_msg_params(notice_content=notice_content,
                                      notice_content_type=notice_content_type,
                                      notice_object=notice_object,
                                      notice_object_type="template")
        try:
            response = requests.post(
                url=self.msg_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            response.raise_for_status()
            res = response.json()

        except:
            print(f"post请求url:{self.msg_url},params:{params} 异常:{traceback.format_exc()}")
            return None
        else:
            if int(res["result"]) == 1:
                return True
            print(f"post请求url:{self.msg_url}出现异常,异常信息:{res['desc']}")
            return None

    def send_msg_by_account(self,
                            notice_content,
                            notice_object,
                            notice_content_type="text"):
        """
         :Description: 发送微信用户消息
         :param notice_content: 消息内容
         :param notice_content_type: 消息内容类型
         :param notice_object: 消息接收对象
         :return 成功为True 失败 None
         :last_editors: LinGuilin
         """

        params = self._get_msg_params(notice_content=notice_content,
                                      notice_content_type=notice_content_type,
                                      notice_object=notice_object,
                                      notice_object_type="account")

        try:
            response = requests.post(
                url=self.msg_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            response.raise_for_status()
            res = response.json()

        except:
            print(f"post请求url:{self.msg_url},params:{params} 异常:{traceback.format_exc()}")
            return
        else:
            if int(res["result"]) == 1:
                return True
            print(f"post请求url:{self.msg_url}出现异常,异常信息:{res['desc']}")
            return None
