#!/usr/bin/env python3.7
# _*_ coding:utf-8 _*_
# 设置全局变量来跨文件获取数据
import gc
import os
import sys

_global_dict = {}
sys.path.append(os.path.dirname(__file__))


def init():
    global _global_dict


def set_value(name, value):
    _global_dict[name] = value


def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue


def del_value():
    for key in list(globals().keys()):
        if not key.startswith("__"):  # 排除系统内建函数
            globals().pop(key)
            del key
            gc.collect()
