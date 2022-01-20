# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2022-01-05 17:32:29
@LastEditTime: 2022-01-13 14:57:05
@LastEditors: HuangJianYi
@Description: 消息推送业务模型
"""

from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.libs.customize.wechat_helper import *


class PushBaseModel():
    """
    :description: 消息推送业务模型
    """
    def __init__(self, context=None, logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def add_wechat_subscribe(self,app_id,open_id):
        """
        :description: 添加微信订阅次数
        :param app_id：应用标识
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        redis_init = SevenHelper.redis_init()
        redis_key = f"wechat_subscribe_list:{app_id}"
        redis_init.zincrby(redis_key, value=open_id, amount=1)
        redis_init.expire(redis_key,3600*24*30)
        return invoke_result_data

    def push_wechat_message(self, open_id, template_id, page, request_data, miniprogram_state="formal", lang="zh_CN", app_id="", app_secret="", plan_id=0):
        """
        :description: 推送微信订阅信息
        :param open_id:接收者（用户）的 openid
        :param template_id:所需下发的订阅模板id
        :param page:点击模板卡片后的跳转页面，仅限本小程序内的页面。支持带参数,（示例index?foo=bar）。该字段不填则模板无跳转
        :param request_data:模板内容，格式形如 { “date2”: { “value”: any }, “thing3”: { “value”: any } }
        :param miniprogram_state:跳转小程序类型：developer为开发版；trial为体验版；formal为正式版；默认为正式版
        :param lang:进入小程序查看”的语言类型，支持zh_CN(简体中文)、en_US(英文)、zh_HK(繁体中文)、zh_TW(繁体中文)，默认为zh_CN
        :param app_id:app_id
        :param app_secret:app_secret
        param plan_id:计划标识
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            push_log_dict = {}
            push_log_dict["open_id"] = open_id
            push_log_dict["template_id"] = template_id
            push_log_dict["page"] = page
            push_log_dict["request_data"] = request_data
            push_log_dict["miniprogram_state"] = miniprogram_state
            push_log_dict["lang"] = lang
            push_log_dict["app_id"] = app_id
            push_log_dict["app_secret"] = app_secret
            push_log_dict["plan_id"] = plan_id
            subscribe_redis_key = f"wechat_subscribe_list:{app_id}"
            if not redis_init.zscore(subscribe_redis_key):
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "订阅次数不足"
            else:
                redis_init.zincrby(subscribe_redis_key, value=open_id, amount=-1)
                invoke_result_data = WeChatHelper.send_template_message(open_id, template_id, page, request_data, app_id=app_id, app_secret=app_secret)
            push_log_dict["result"] = invoke_result_data
            push_redis_key = f"wechat_push_list:{app_id}"
            if plan_id > 0:
                push_redis_key += f"_{plan_id}"
            redis_init.rpush(push_redis_key, SevenHelper.json_dumps(push_log_dict))
            redis_init.expire(push_redis_key, 3600 * 24 * 30)
            return invoke_result_data
        except Exception as ex:
            if self.context:
                self.context.logging_link_error("【推送微信订阅信息】" + traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error("【推送微信订阅信息】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"
        return invoke_result_data
