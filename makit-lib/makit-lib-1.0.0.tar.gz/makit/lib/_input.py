#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：kevinleong1011@hotmail.com
@desc: 
"""

__all__ = [
    'Input',
    'InputError'
]


class Input:
    @classmethod
    def get(cls, prompt, default=None, ign_case=False):
        """
        获取控制台输入，如果忽略大小写，则返回被转换为小写的输入
        :param prompt: 提示文字
        :param default: 没有输入时的默认值
        :param ign_case: 是否忽略大小写，默认False
        :return:
        """
        v = input(prompt)
        if ign_case:
            v = v.lower()
        return v or default

    @classmethod
    def bool(cls, prompt, default=True, true_options=None, false_options=None):
        """
        将控制台输入转换为布尔值返回
        :param prompt: 提示文字
        :param default: 默认True
        :param true_options: 允许转换为True的输入，默认：true, yes, y, 1
        :param false_options: 允许转换为False的输入，默认：false, no, n, 0
        :return: 如果无法按要求被转换，将返回原输入
        """
        if true_options is None:
            true_options = ['true', '1', 'yes', 'y']
        v = input(prompt).strip().lower()
        if v in true_options:
            return True
        elif v in false_options:
            return False
        else:
            return default

    @classmethod
    def int(cls, prompt, default=0):
        """
        将控制台输入转换为整型值
        :param prompt: 提示文字
        :param default: 默认为0
        :return:
        """
        v = input(prompt).strip()
        if not v:
            return default
        return int(v)

    @classmethod
    def float(cls, prompt, default=0.0):
        """
        将控制台输入转换为浮点值
        :param prompt: 提示文字
        :param default: 默认为0
        :return:
        """
        v = input(prompt).strip()
        if not v:
            return default
        return float(v)


class InputError(Exception):
    """"""
