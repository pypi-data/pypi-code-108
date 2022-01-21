#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @Time    : 2020/2/28 16:15
#  @Author  : Evan.hu
#  @File    : operation_json

import jsonpath

class OperetionJson(object):
    def __init__(self, text):
        self.text = text

    # 根据传入字段获取json的值
    def get_value(self, name):
        # 当不存在name这个key时，返回false
        data = jsonpath.jsonpath(self.text, '$..{name}'.format(name=name))
        return data