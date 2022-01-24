# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2021-03-12 15:16:39
:LastEditors: ChenXiaolei
:Description: uuid helper
"""
import uuid


class UUIDHelper:
    @classmethod
    def get_uuid(self):
        """
        :Description: 获取uuid4
        :return: uuid字符串
        :last_editors: ChenXiaolei
        """
        return str(uuid.uuid4())