# coding=utf-8
"""
@Author: Liang Chao
@Email: kevinleong1011@hotmail.com
@Desc:
"""
import json
import re
from typing import Union

import yaml


def _get_item(o, item, default=None, raise_error=False):
    try:
        return o[item]
    except (KeyError, IndexError):
        if raise_error:
            raise
        return default


def _parse_node(node):
    key, index = node, None
    p = re.compile(r'(\w+)?\[(\d+)]')
    matches = p.findall(node)
    if matches:
        key, index = matches[0][0], int(matches[0][1])
    return key, index


class Json:
    """
    包装dict和list
    """

    def __init__(self, data: Union[dict, list]):
        self.data = data
        self.__callbacks = []

    def items(self):
        if isinstance(self.data, dict):
            return self.data.items()
        else:
            return self.data

    def walk(self, path=None):
        """
        遍历所有路径值
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
                    for _item in _walk(v, p=p + '/' + k):
                        yield _item
            else:
                yield p, d

        data = self.get(path)
        for _o in _walk(data, path or ''):
            yield _o

    def get(self, path=None, default=None, raise_error=False):
        """
        获取路径值
        :param path: 字符串路径，如 books/0/name
        :param default: 路径不存在时的默认值
        :param raise_error: 路径不存在时是否抛出异常
        :return:
        """
        if not path:
            return self.data
        nodes = path.split('/')
        cur = self.data
        for node in nodes:
            is_int = re.match(r'^\d+$', node) is not None
            if isinstance(cur, list):
                assert is_int, f'Invalid path: {path}'
                node = int(node)
                cur = cur[node]
            elif isinstance(cur, dict):
                v = cur.get(node)
                if v is None and is_int:
                    v = cur.get(int(node))
                cur = v
            if cur is None:
                break
        if cur is None:
            if raise_error:
                raise Exception(f'Path not found: {path}')
            return default
        return cur

    def set(self, path, value):
        """
        设置路径值
        :param path: 路径
        :param value: 值
        :return:
        """
        items = path.strip('/').split('/') or []
        prev, cur = None, self.data
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
        elif isinstance(item, int):
            cur.insert(item, value)

        self.__callback(**{path: value})

    def update(self, **kwargs):
        if isinstance(self.data, dict):
            self.data.update(**kwargs)
        else:
            self.data.append(kwargs)
        self.__callback(**kwargs)

    def merge(self, other):
        """
        合并数据
        :param other:
        :return:
        """
        if isinstance(other, (list, dict)):
            other = Json(other)
        assert isinstance(other, Json), '被合并的对象只能是list/dict/Json'
        for p, v in other.walk():
            self.set(p, v)
        return self

    def on_change(self, callback):
        """
        添加修改回调
        :param callback:
        :return:
        """
        self.__callbacks.append(callback)

    def __getattr__(self, name):
        v = self.get(name)
        if isinstance(v, (list, dict)):
            return Json(v)
        return v

    def __getitem__(self, item):
        if isinstance(self.data, list):
            v = self.data[item]
        else:
            v = self.data[item]
        if isinstance(v, (dict, list)):
            return Json(v)
        else:
            return v

    def __setitem__(self, key, value):
        if isinstance(self.data, list):
            self.data.insert(key, value)
        else:
            self.data[key] = value
        self.__callback(**{key: value})

    def __callback(self, **kwargs):
        for cb in self.__callbacks:
            cb(self, **kwargs)

    @classmethod
    def load(cls, file):
        with open(file, 'r', encoding='utf-8') as f:
            return Json(json.load(f))

    @staticmethod
    def loads(s, *, cls=None, object_hook=None, parse_float=None,
              parse_int=None, parse_constant=None, object_pairs_hook=None, **kw):
        """"""
        data = json.loads(s, cls=cls, object_hook=object_hook, parse_float=parse_float, parse_int=parse_int,
                          parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
        return Json(data)

    def load_yml(self, file, encoding='utf-8'):
        data = yaml.load(open(file, 'r', encoding=encoding), Loader=yaml.FullLoader)
        self.data = data
        return self

    def __contains__(self, item):
        if isinstance(self.data, list):
            return len(self.data) > item
        else:
            return item in self.data

    def __str__(self):
        return self.data
