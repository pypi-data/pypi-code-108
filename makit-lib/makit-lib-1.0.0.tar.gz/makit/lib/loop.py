# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""
import sys
import time

from . import fn


class Repeat:
    """
    循环
    """

    def __init__(self, max_times=None, interval=0, duration=None):
        """

        :param max_times: 最大次数
        :param interval: 循环间隔
        :param duration: 持续时长
        """
        self.max_times = max_times or sys.maxsize
        self.interval = interval  # 循环间隔
        self.duration = duration  # 持续时长
        self._callback = None
        self._callback_args = []
        self._callback_kwargs = {}
        self._ign_errors = None
        self.__raise = True

    @property
    def silent(self):
        """
        忽略所有异常
        :return:
        """
        self._ign_errors = Exception
        self.__raise = False
        return self

    def ignore(self, *errors):
        """
        忽略指定异常
        :param errors:
        :return:
        """
        self._ign_errors = errors
        self.__raise = False
        return self

    def callback(self, func, *args, **kwargs):
        """
        回调函数
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        self._callback = func
        self._callback_args = args
        self._callback_kwargs = kwargs
        return self

    def call(self, func, *args, **kwargs):
        """
        循环调用函数
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        for i in repeat(self.max_times, self.duration):
            try:
                result = func(*args, **kwargs)
                if self._callback:
                    self._callback(i, result, *self._callback_args, **self._callback_kwargs)
            except self._ign_errors or Exception:
                if self.__raise:
                    raise

    def until(self, condition_fn, *args, **kwargs):
        """
        循环直到条件满足
        :param condition_fn: 条件函数
        :param args:
        :param kwargs:
        :return:
        """
        for i in repeat(self.max_times, self.duration):
            try:
                if fn.run(condition_fn, *args, **kwargs, i=i):
                    return True
            except self._ign_errors or Exception:
                if self.__raise:
                    raise
            time.sleep(self.interval)
        return False


def loop(max_times=None, interval=0):
    """
    用于循环调用函数或循环直到某个条件满足
    :param max_times:
    :param interval:
    :return:
    """
    return Loop(max_times, interval)


class LoopBreakError(Exception):
    """"""


Loop = Repeat


def repeat(max_times=None, duration=None):
    """
    用于重复执行，至少执行一次
    :param max_times: 最大重复次数
    :param duration: 最大执行时长
    :return:
    """
    start = time.time()
    i = 0
    while True:
        if max_times and i >= max_times:
            break
        if duration and time.time() - start > duration:
            break
        yield i
        i += 1
