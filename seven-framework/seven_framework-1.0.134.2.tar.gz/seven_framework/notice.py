# -*- coding: utf-8 -*-
"""
:Author: YuMinJie
:Date: 2020-05-15 11:16:28
:LastEditTime: 2020-06-10 14:04:27
:LastEditors: ChenXiaolei
:Description: 消息帮助类
"""


import requests
import platform
import os


class NoticeHelper(object):

    """
    :Description: 企业微信群机器人消息
    """

    def __init__(self, webhook_key='', project_name=None):

        if webhook_key and webhook_key != '':
            # 参数获取
            # 传入webhook秘钥
            self.webhook_key = webhook_key

        if not project_name:
            if platform.system() == "Windows":
                self.project_name = os.getcwd().split('\\')[-1]
            else:
                self.project_name = os.getcwd().split('/')[-1]
        else:
            self.project_name = project_name

    def _get_webhook_key(self, webhook_key=''):
        """
        :Description: 获取webhook_key，判断传参webhook_key是否为空字符串，如果为空字符串则从初始化属性获取
        :param webhook_key: webhook密钥，默认值为空字符串
        :return: webhook_key

        """
        if not webhook_key or webhook_key == '':
            if not hasattr(self, "webhook_key") or self.webhook_key == '':
                raise Exception("webhook_key is not configured")
            return self.webhook_key
        return webhook_key

    def send_webhook(self, text='', mentioned_list=[], mentioned_mobile_list=[], webhook_key=''):
        """
        :Description: 发送企业微信消息
        :param webhook_key: webhook秘钥
        :param text:消息文本
        :param mentioned_list:工号、企业微信名或者@all
        :param mentioned_mobile_list:传入手机号或者@all
        :return: 企业微信消息

        """

        webhook_key = self._get_webhook_key(webhook_key)
        # 数据合成

        url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + webhook_key
        body = {"msgtype": "text", "text": {"content": f"【{self.project_name}】{text}",
                                            "mentioned_list": mentioned_list, 'mentioned_mobile_list': mentioned_mobile_list}}

        try:
            response = requests.post(url, json=body, auth=(
                "Content-Type", "application/json"))
        except Exception as ex:
            pass
