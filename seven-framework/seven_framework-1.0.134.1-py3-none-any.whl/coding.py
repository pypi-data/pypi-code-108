# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-05-11 21:46:17
:LastEditTime: 2021-03-22 18:11:50
:LastEditors: ChenXiaolei
:Description: 编码类型组件
"""

from urllib import parse


class CodingHelper():
    @classmethod
    def url_encode(self, text, coding='utf-8'):
        """
        :description: URL编码
        :param text: 需编码的字符串
        :param coding: 编码集规则(默认utf-8)
        :return url_encode后的字符串
        :last_editors: ChenXiaolei
        """
        return parse.quote_plus(text, encoding=coding)

    @classmethod
    def url_decode(self, text, coding='utf-8'):
        """
        :description: URL解码
        :param text: 需解码的字符串
        :param coding: 编码集规则(默认utf-8)
        :return url_decode后的字符串
        :last_editors: ChenXiaolei
        """
        return parse.unquote(text, encoding=coding)
