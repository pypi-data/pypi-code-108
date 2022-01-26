# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""
import threading
from functools import wraps


def synchronized(func):
    """
    装饰器，用于方法加锁
    :param func:
    :return:
    """
    func.__lock__ = threading.Lock()

    @wraps(func)
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func
