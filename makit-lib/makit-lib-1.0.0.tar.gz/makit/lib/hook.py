#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：kevinleong1011@hotmail.com
@desc: 
"""
import inspect
from types import FunctionType, ModuleType, MethodType

__all__ = [
    'HookCaller',
    'HookError',
    'HookProperty'
]

from makit.lib import fn, py


class HookCaller:
    """
    钩子调用器
    """

    def __init__(self):
        self.__hooks = []
        self.__calling_records = {}

    def __getattr__(self, item):
        try:
            v = super().__getattribute__(item)
            return v
        except AttributeError:
            self._method = item
            return self

    def __iter__(self):
        for hook in self.__hooks:
            yield hook

    def __call__(self, *args, first_result=False, once_run=False, **kwargs):
        if once_run and self.__calling_records.get(self._method):
            return
        results = []
        for hook in self.__hooks:
            method = getattr(hook, self._method, None)
            result = fn.run(method, *args, **kwargs)
            if once_run:
                self.__calling_records[self._method] = True
            if first_result:
                return result
            results.append(result)
        return results

    def add(self, obj):
        if isinstance(obj, str):
            obj = py.get_object(obj)
        if inspect.ismodule(obj) or inspect.isclass(obj) or inspect.isroutine(obj):
            self.__hooks.append(obj)
        else:
            raise HookError(f'不支持的钩子：{obj}')


class HookProperty:
    def __init__(self):
        self._instance = None
        self.__hooks = []

    def __get__(self, instance, owner):
        self._instance = instance
        return self.__hooks

    def __set__(self, instance, value):
        self._instance = instance
        if isinstance(value, (tuple, list)):
            for hook in value:
                if hook not in self.__hooks:
                    self.__hooks.append(hook)
        elif isinstance(value, (str, FunctionType, ModuleType, type, MethodType)):
            if value not in self.__hooks:
                self.__hooks.append(value)
        else:
            raise HookError(f'不支持的钩子：{value}')


class HookError(Exception):
    """"""
