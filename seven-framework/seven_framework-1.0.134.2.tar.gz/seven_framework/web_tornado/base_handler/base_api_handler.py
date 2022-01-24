# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-03-06 23:17:54
:LastEditTime: 2021-11-17 15:56:40
:LastEditors: ChenXiaolei
:Description: Handler基础类(api)
"""

# seven_framework import
from .base_handler import *


class BaseApiHandler(BaseHandler):
    """
    :Description: api base handler. not session
    :last_editors: ChenXiaolei
    """
    def __init__(self, *argc, **argkw):
        """
        :Description: 初始化
        :last_editors: ChenXiaolei
        """
        super(BaseApiHandler, self).__init__(*argc, **argkw)

    def write_error(self, status_code, **kwargs):
        """
        :Description: 重写全局异常事件捕捉
        :last_editors: ChenXiaolei
        """
        self.logger_error.error(
            traceback.format_exc(),
            extra={"extra": {
                "request_code": self.request_code if hasattr(self,"request_code") else ""
            }})
        return self.response_json_error()

    def prepare_ext(self):
        """
        :Description: 置于任何请求方法前被调用扩展
        :last_editors: ChenXiaolei
        """
        pass
