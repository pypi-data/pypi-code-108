#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :QueryException.py
# @Time      :2021/4/25 4:59 下午
# @Author    :meng.lv


class QueryException(BaseException):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "%s : %s" % (self.data['returnCode'], self.data['returnMsg'])
