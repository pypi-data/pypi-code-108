# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""
import sys
import time


class Timeout:
    """
    超时
    """

    def __init__(self, seconds=None, interval=0):
        """
        构造函数
        :param seconds: 超时时间，单位秒
        :param interval: 循环间隔
        """
        self.seconds = seconds or sys.maxsize
        self.interval = interval
        self._silent = False
        self._ign_errors = None

    @property
    def silent(self):
        """
        忽略所有异常
        :return: 返回自身
        """
        self._silent = True
        return self

    def ignore(self, *errors):
        """
        忽略指定异常
        :param errors:
        :return:
        """
        self._ign_errors = errors
        self._silent = True
        return self

    def call(self, fn, *args, **kwargs):
        """
        调用函数
        :param fn:
        :param args:
        :param kwargs:
        :return:
        """
        start = time.time()
        while time.time() - start < self.seconds:
            try:
                return fn(*args, **kwargs)
            except self._ign_errors or Exception:
                if not self._silent:
                    raise
            time.sleep(self.interval)

    def until(self, condition, *args, **kwargs):
        """
        验证条件直到超时
        :param condition:
        :param args:
        :param kwargs:
        :return:
        """
        start = time.time()
        while time.time() - start < self.seconds:
            try:
                if condition(*args, **kwargs):
                    return True
            except self._ign_errors or Exception:
                if not self._silent:
                    raise
            time.sleep(self.interval)
        return False


def timeout(seconds=None, interval=None):
    """
    超时，用法：timeout(20, 0.5).silent.call(fn, *args, **kwargs)
    :param seconds:
    :param interval:
    :return:
    """
    return Timeout(seconds, interval)
