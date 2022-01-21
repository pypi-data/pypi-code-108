# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2020/2/29 18:02
# @Author: "John"
import json


def beautiful_output_dict(d, encoding='utf-8', indent=4, sort_keys=True, ensure_ascii=False):
    """
        将 Python 的字典， 以展开的方式输出
    :param d: 要处理的字典
    :param encoding: 编码方式，默认 utf-8
    :param indent:  缩进
    :param sort_keys: 根据字典的 key 进行排序
    :param ensure_ascii:
    :return:
    """
    return json.dumps(json.loads(d, encoding=encoding), sort_keys=sort_keys, indent=indent, ensure_ascii=ensure_ascii)
