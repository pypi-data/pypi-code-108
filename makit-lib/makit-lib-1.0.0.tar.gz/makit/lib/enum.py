# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""


def from_value(enum_type, value):
    """
    从枚举值获取枚举，一般用于反向转换
    :param enum_type:
    :param value:
    :return:
    """
    members = enum_type.__members__
    for k, v in members.items():
        if value == v.value:
            return v


def from_name(enum_type, name, return_default=False):
    """
    根据名称获取枚举对象，一般用于反向转换
    :param enum_type:
    :param name:
    :param return_default:
    :return:
    """
    members = enum_type.__members__
    first_member = None
    for k, v in members.items():
        if not first_member:
            first_member = v
        if k == name:
            return v
    if return_default:
        return first_member
