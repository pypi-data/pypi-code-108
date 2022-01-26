# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Created: 2022/1/25
@Desc: 
"""
import threading

from ._time import Timeout
from ._data import Data
from ._serialize import serialize
from ._dict import *
from ._input import *
from ._json import *


def singleton(o):
    """
    对类添加单例装饰，不需要专门写__new__实现，也不影响自己的__new__
    """
    o._instance = None
    o._lock = threading.Lock()

    origin_new = getattr(o, '__new__', None)
    origin_init = getattr(o, '__init__', None)

    def class_new(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = object.__new__(cls)
                cls._instance._initialized = False

            if origin_new:
                origin_new(cls, *args, **kwargs)
            return cls._instance

    o.__new__ = class_new

    # 这里保证实例初始化只会执行一次，否则即使保证了实例也无法保证实例内部数据
    def init(self, *args, **kwargs):
        if not self._initialized:
            origin_init(self, *args, **kwargs)
            self._initialized = True

    o.__init__ = init

    return o
