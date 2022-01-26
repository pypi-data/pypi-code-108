# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Created: 2022/1/9
@Desc: 
"""
import json

import yaml

from . import jsonpath


class Data:
    def __init__(self, *args, **kwargs):
        if args and kwargs:
            raise RuntimeError('Data only can be list or dict')
        if args:
            object.__setattr__(self, 'd', [*args])
        else:
            object.__setattr__(self, 'd', kwargs)

    def __getattr__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            v = self.d.get(item)
            return self.wrap(v)

    def __setattr__(self, key, value):
        if isinstance(self.d, (dict, list)):
            self.d[key] = value

    def __getitem__(self, item):
        v = self.d[item]
        return self.wrap(v)

    def __setitem__(self, key, value):
        self.d.__setitem__(key, value)

    def __contains__(self, item):
        return item in self.d

    def __delitem__(self, key):
        self.d.__delitem__(key)

    def __len__(self):
        return len(self.d)

    def __repr__(self):
        return repr(self.d)

    @classmethod
    def wrap(cls, value):
        if isinstance(value, dict):
            return Data(**value)
        elif isinstance(value, (list, tuple)):
            return Data(*value)
        return value

    def items(self):
        if isinstance(self.d, dict):
            return self.d.items()
        else:
            return self.d

    def walk(self, path=None):
        return jsonpath.walk(self.d, path)

    def get(self, path=None, default=None, raise_error=False):
        return jsonpath.get(self.d, path, default=default, raise_error=raise_error)

    def set(self, path, value):
        jsonpath.update(self.d, path, value)

    def merge(self, other):
        if isinstance(other, Data):
            object.__setattr__(self, 'd', jsonpath.merge(self.d, other.d))
        elif isinstance(other, (list, dict)):
            object.__setattr__(self, 'd', jsonpath.merge(self.d, other))

    def load_module(self, module):
        for name in dir(module):
            if name.startswith('_'):
                continue
            v = getattr(module, name)
            self[name] = v

    def load_yml(self, file, encoding='utf-8'):
        data = yaml.load(open(file, 'r', encoding=encoding), Loader=yaml.FullLoader)
        object.__setattr__(self, 'd', data)
        return self

    @staticmethod
    def loads(s, *, cls=None, object_hook=None, parse_float=None,
              parse_int=None, parse_constant=None, object_pairs_hook=None, **kw):
        """"""
        data = json.loads(s, cls=cls, object_hook=object_hook, parse_float=parse_float, parse_int=parse_int,
                          parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
        return Data.wrap(data)

    @staticmethod
    def load(file):
        with open(file, 'r', encoding='utf-8') as f:
            return Data.wrap(json.load(f))
