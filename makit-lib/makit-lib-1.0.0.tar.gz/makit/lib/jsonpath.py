#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liangchao@noboauto.com
@desc: 
"""
import re
from copy import deepcopy


def get(data, path=None, default=None, raise_error=False):
    """
    获取路径值
    :param data: 字典或者列表数据
    :param path: 字符串路径，如 books/0/name
    :param default: 路径不存在时的默认值
    :param raise_error: 路径不存在时是否抛出异常
    :return:
    """
    if not path:
        return data
    nodes = path.split('/')
    cur = data
    for node in nodes:
        is_int = re.match(r'^\d+$', node) is not None
        if isinstance(cur, list):
            assert is_int, f'Invalid path: {path}'
            node = int(node)
            cur = cur[node]
        elif isinstance(cur, dict):
            v = dict.get(cur, node)
            if v is None and is_int:
                v = dict.get(cur, int(node))
            cur = v
        if cur is None:
            break
    if cur is None:
        if raise_error:
            raise Exception(f'Path not found: {path}')
        return default
    return cur


def update(data, path, value):
    items = path.strip('/').split('/') or []
    prev, cur = None, data
    item = None
    while items:
        prev = cur
        item = items.pop(0)
        if re.match(r'^\d+$', item):
            item = int(item)
        elif re.match(r"^'\d+'$", item):
            item = item[1:-1]
        try:
            cur = cur[item]
        except (IndexError, KeyError):
            break
    else:
        cur = prev
        cur[item] = value
        return
    while items:
        last = items.pop(-1)
        if re.match(r'^\d+$', last):
            last = int(last)
        elif re.match(r"^'\d+'$", last):
            last = last[1:-1]
        if isinstance(last, str):
            value = {last: value}
        else:
            pass
    if isinstance(item, str):
        cur[item] = value
    elif isinstance(item, int) and isinstance(cur, list):
        cur.insert(item, value)
    elif isinstance(item, int) and isinstance(cur, dict):
        cur[item] = value


def walk(data, path=None):
    """
    遍历所有路径值
    :param data:
    :param path:
    :return:
    """

    def _walk(d, p):
        if isinstance(d, list):
            i = 0
            for item in d:
                for o in _walk(item, p + '/' + str(i)):
                    yield o
                i += 1
        elif isinstance(d, dict):
            for k, v in d.items():
                for _item in _walk(v, p=p + '/' + str(k)):
                    yield _item
        else:
            yield p.strip('/'), d

    data = data.get(path) if path else data
    for _o in _walk(data, path or ''):
        yield _o


def merge(data, other):
    """
    合并数据
    :param data:
    :param other:
    :return:
    """
    assert isinstance(other, (list, dict))
    assert type(data) == type(other), f'需要合并的数据类型不一致！'
    result = deepcopy(data)
    for p, v in walk(other):
        update(result, p, v)
    return result
