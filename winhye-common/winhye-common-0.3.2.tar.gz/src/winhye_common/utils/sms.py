# -*- coding: utf-8 -*-
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models


class Sample:
    def __init__(self, access_key_id, access_key_secret):
        self.access_key_secret = access_key_secret
        self.access_key_id = access_key_id

    @staticmethod
    def create_client(access_key_id: str, access_key_secret: str, ) -> Dysmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = 'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    # 同步发送
    def send_sms(self, phone_numbers, sign_name, template_code, template_param):
        """
        :param phone_numbers:要发送的手机号
        :param sign_name:短信签名名称
        :param template_code:短信模板ID
        :param template_param:短信模板变量对应的实际值
        :return:
        """
        client = Sample.create_client(self.access_key_id, self.access_key_secret)
        # 分别为 AccessKey ID AccessKey Secret
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=phone_numbers,  # 要发送的手机号  必填
            sign_name=sign_name,  # 短信签名名称  必填
            template_code=template_code,  # 短信模板ID  必填
            template_param=template_param,  # 短信模板变量对应的实际值
            # sms_up_extend_code='',  # 上行短信扩展码
            # out_id=''  # 外部流水扩展字段
        )
        # 复制代码运行请自行打印 API 的返回值
        return client.send_sms(send_sms_request)
