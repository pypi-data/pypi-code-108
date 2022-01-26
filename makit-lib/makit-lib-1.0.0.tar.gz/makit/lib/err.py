#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liangchao@noboauto.com
@desc: 
"""
import sys
import traceback
from contextlib import contextmanager
from typing import List

from .logging import logger


@contextmanager
def ignore_errors(*errors):
    """
    忽略异常
    :param errors:
    :return:
    """
    try:
        yield
    except errors or Exception:
        logger.debug(f'Ignore following error:\n{traceback.format_exc()}')


class ErrorCallback:
    """
    错误回调
    """

    def __init__(self):
        self.listening_types = []
        self.fn = None
        self.fn_args = []
        self.fn_kwargs = {}
        self.capture = None

    def listen(self, *errors):
        self.listening_types = errors
        return self

    def call(self, fn, args=None, kwargs=None):
        self.fn = fn
        self.fn_args = args or []
        self.fn_kwargs = kwargs or {}
        return self

    def __call__(self):
        if self.fn:
            self.fn(*self.fn_args, **self.fn_kwargs)


class ErrorCapture:
    """
    错误捕捉器，可用于统一异常处理
    """

    def __init__(self):
        self.errors = []
        self.callbacks: List[ErrorCallback] = []

    @contextmanager
    def __call__(self, *errors, raise_error=False):
        try:
            yield
        except (errors or Exception) as e:
            exc_info = sys.exc_info()
            self.errors.append(exc_info)
            for callback in self.callbacks:
                if e.__class__ in callback.listening_types:
                    callback()
            if raise_error:
                raise

    def listen(self, *errors):
        """
        监听错误异常类型
        :param errors: 异常类型
        :return:
        """
        callback = ErrorCallback().listen(*errors)
        self.callbacks.append(callback)
        return callback
