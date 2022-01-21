# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2021-07-15 14:09:43
@LastEditTime: 2021-08-10 16:42:18
@LastEditors: HuangJianYi
:description: 通用Handler
"""
from seven_framework.config import *
from seven_framework.redis import *
from seven_framework.web_tornado.base_handler.base_api_handler import *

from seven_cloudapp_frame.handlers.frame_base import *


class IndexHandler(FrameBaseHandler):
    """
    :description: 默认页
    """
    def get_async(self):
        """
        :description: 默认页
        :param 
        :return 字符串
        :last_editors: HuangJianYi
        """
        self.write(UUIDHelper.get_uuid() + "_" + config.get_value("run_port") + "_api")