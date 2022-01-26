#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liangchao@noboauto.com
@desc: 
"""
import json
import os
import re
from types import ModuleType

from makit.lib import jsonpath

ENTER_CHARS = '\r\n\x85\u2028\u2029'


# region 转换器

def convert_value(value):
    if re.match(r'^\d+$', value):
        return int(value)
    elif value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    return value


def boolean(value):
    lower_value = value.lower()
    return True if lower_value == 'true' else False if lower_value == 'false' else None


def integer(value):
    """
    转换为整数
    :param value:
    :return:
    """
    if re.match(r'^\d+$', value):
        return int(value)


def cvt_float(digits=None):
    """
    转换为浮点数
    :param digits: 保留位数
    :return:
    """

    def cvt(value):
        if re.match(r'^\d*\.\d+$', value):
            v = float(value)
            if digits is None:
                return v
            else:
                return round(v, digits)

    return cvt


# endregion

class Line:
    """
    行
    """

    def __init__(self):
        self.content = ''
        self.indent = None  # 缩进
        self.parent = None

    def append(self, c):
        self.content += c
        if c != ' ' and self.indent is None:
            self.indent = int((len(self.content) - 1) / 2)

    @property
    def valid(self):
        return self.content not in ['', None]

    def startswith(self, s):
        return self.content.startswith(s)

    def endswith(self, s):
        return self.content.endswith(s)

    def __repr__(self):
        return f'<Line {self.content}>'


class Parser:
    """
    解析器基类
    """

    def read_stream(self, stream):
        with stream:
            line = Line()
            while True:
                c = stream.read(1)
                if not c:
                    break
                if c in ENTER_CHARS:
                    self.handle_line(line)
                    line = Line()
                else:
                    line.append(c)
            self.handle_line(line)

    def handle_line(self, line):
        raise NotImplementedError

    def convert_value(self, value):
        raise NotImplementedError


class YmlParser(Parser):
    def handle_line(self, line):
        pass

    def convert_value(self, value):
        pass


class IniParser(Parser):
    def __init__(self):
        self._data = {}
        self._sections = {}
        self.__cur_section = None

    @property
    def sections(self):
        return self._sections

    def readfile(self, filename, encoding='utf-8'):
        fs = open(filename, 'r', encoding=encoding)
        self.read_stream(fs)
        return self._data

    def writefile(self, filename, encoding='utf-8'):
        pass

    def handle_line(self, line):
        if not line.content or line.content.startswith(';'):
            return
        if line.startswith('[') and line.endswith(']'):
            section = line.content[1:-1]
            self.__cur_section = self._data.setdefault(section, {})
            self._sections[section] = self.__cur_section
        else:
            key, value = line.content.split('=', maxsplit=1)
            value = self.convert_value(value.strip())
            if self.__cur_section is None:
                self._data[key.strip()] = value
            else:
                self.__cur_section[key.strip()] = value

    def convert_value(self, value):
        value_lower = value.lower()
        if value_lower == 'true':
            return True
        elif value_lower == 'false':
            return False
        elif re.match(r'^\d+$', value):
            return int(value)
        elif re.match(r'^\d+\.\d+$', value):
            return float(value)
        return value

    def path(self, path):
        return jsonpath.get(self._data, path)


class PropertyParser(Parser):
    def handle_line(self, line):
        pass

    def convert_value(self, value):
        pass


class ConfParser(Parser):
    def handle_line(self, line):
        pass

    def convert_value(self, value):
        pass


class Config:
    """
    配置类，支持配置继承
    """

    def __init__(self, **kwargs):
        self._data = kwargs
        self.parents = []  # 父级配置

    def get(self, path, default=None):
        """
        获取配置项
        :param path: jsonpath支持的配置路径
        :param default: 默认值
        :return:
        """
        v = jsonpath.get(self._data, path)
        if v is None:
            for p in self.parents:
                v = p.get(path)
                if v is not None:
                    return v
        return default if v is None else v

    def load_module(self, module):
        """
        从python的ModuleType对象加载配置
        :param module:
        :return:
        """
        for name in dir(module):
            if name.startswith('_'):
                continue
            v = getattr(module, name)
            self._data[name] = v
        return self

    def load_file(self, filename, encoding='utf-8'):
        if filename.endswith(('.yml', '.yaml')):
            self.load_yml(filename, encoding=encoding)
        elif filename.endswith('.json'):
            self.load_json(filename, encoding=encoding)
        return self

    def load_yml(self, filename, encoding='utf-8'):

        pass

    def load_ini(self, filename):
        pass

    def load_json(self, filename, encoding='utf-8'):
        with open(filename, 'r', encoding=encoding) as f:
            data = json.loads(f.read())
            self._data.update(**data)

    def inherit(self, *others):
        """
        从其他配置继承
        :param others: dict/ModuleType/文件路径
        :return:
        """
        for other in others:
            if isinstance(other, dict):
                other = Config(**other)
            elif isinstance(other, ModuleType):
                other = load_module(other)
            elif isinstance(other, str):
                if os.path.exists(other):
                    other = Config().load_file(other)
                else:
                    raise InvalidConfigError(f'目标不是正确的配置文件：{other}')
            if isinstance(other, Config):
                self.parents.append(other)
        return self


def load_module(module):
    return Config().load_module(module)


class InvalidConfigError(Exception):
    """"""
