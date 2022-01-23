"""
Note:
    Currently, all of the examples for concurrent or coroutine, not for parallel.
"""

from typing import Dict, TypeVar, Generic, Any
from functools import wraps, update_wrapper
import multiprocessing
import threading
import inspect
import random
import time
import sys


T = TypeVar("T")


def simple_singleton(_class):

    __Instance: Generic[T] = None

    def get_instance(*args, **kwargs):
        nonlocal __Instance
        if __Instance is None:
            __Instance = _class(*args, **kwargs)
        return __Instance

    return get_instance



class Singleton:

    _Instances = {}

    def __new__(cls, *args, **kwargs):
        cls_name = cls.__name__
        if cls_name not in cls._Instances.keys():
            cls._Instances[cls_name] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        print(f"[DEBUG] cls._Instances: {cls._Instances}")
        return cls._Instances[cls_name]



class SingletonMeta(type):

    """
    Note:
        It's possible that occur "Rare Error" if this variable saving at class level.
        For every class variables which could be shared between with
        each threads or green threads in concurrent or coroutine.
        However, for parallel, it couldn't shared it because it's be temporaly save in memory.
        For concurrent and coroutine, they could share the value betweem different.
        For parallel, program run in different process and they have their responsibiliy, also they doesn't have any access priority between each others.

    Resolution:
        Resolve issue. It doesn't work anymore because instanciate multiprocessing.Manager much times .
        It needs to instanciate multiprocessing.Manager first and ONCE before we use the relateed features
        like Namespace, dict, Lock or something else.
    """

    _Instance: Generic[T] = None
    _Lock = multiprocessing.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._Lock:
            if cls._Instance is None:
                __super_cls = super(SingletonMeta, cls).__call__(*args, **kwargs)
                cls._Instance = __super_cls
        return cls._Instance



class NamedSingletonMeta(type):

    """
    Note:
        It's possible that occur "Rare Error" if this variable saving at class level.
        For every class variables which could be shared between with
        each threads or green threads in concurrent or coroutine.
        However, for parallel, it couldn't shared it because it's be temporaly save in memory.
        For concurrent and coroutine, they could share the value betweem different.
        For parallel, program run in different process and they have their responsibiliy, also they doesn't have any access priority between each others.

    Resolution:
        Resolve issue. It doesn't work anymore because instantiate multiprocessing.Manager much times .
        It needs to instanciate multiprocessing.Manager first and ONCE before we use the relateed features
        like Namespace, dict, Lock or something else.
    """

    _Instances: Dict = {}
    _Lock = multiprocessing.Lock()

    def __call__(cls, *args, **kwargs):
        _name = kwargs.get("test_name", None)
        if _name is None:
            cls_name = cls.__name__
        else:
            cls_name = _name
        with cls._Lock:
            if cls_name not in cls._Instances:
                __super_cls = super(NamedSingletonMeta, cls).__call__(*args, **kwargs)
                cls._Instances[cls_name] = __super_cls
        print(f"[DEBUG] cls._Instances: {cls._Instances}")
        return cls._Instances[cls_name]



def singleton(_class):

    if inspect.isclass(_class) is False:
        raise ValueError("The target object be decorated should be a 'class' type object.")

    class _SingletonClass(_class):

        _Instance: Generic[T] = None

        def __new__(_class, *args, **kwargs):
            if _SingletonClass._Instance is None:
                _SingletonClass._Instance = super(_SingletonClass, _class).__new__(_class, *args, **kwargs)
                _SingletonClass._Instance._sealed = False
            return _SingletonClass._Instance


        def __init__(self, *args, **kwargs):
            if _SingletonClass._Instance._sealed:
                return
            super(_SingletonClass, self).__init__(*args, **kwargs)
            _SingletonClass._Instance._sealed = True

    _SingletonClass.__name__ = _class.__name__
    _SingletonClass.__doc__ = _class.__doc__
    _SingletonClass.__str__ = _class.__str__
    _SingletonClass.__repr__ = _class.__repr__

    return _SingletonClass



def namedsingleton(cls=None, name: str = ""):
    """
    Note:
        For parallel, this decorator doesn't work finely because of PickleError.
        This decorator only work for concurrent and coroutine.
    :param cls:
    :param name:
    :return:
    """

    if cls:
        return _NamedSingleton(_class=cls, name=name)
    else:
        @wraps(cls)
        def _(cls):
            return _NamedSingleton(_class=cls, name=name)
        return _



def _NamedSingleton(_class, name: str):

    if inspect.isclass(_class) is False:
        raise ValueError("The target object be decorated should be a 'class' type object.")

    if name is None:
        raise ValueError("Option *name* could not be None value.")
    _Instance_Name = name

    # @test_cls_wrapper(_class)
    class _SingletonClass(_class):

        _Instances: Dict[str, Any] = {}
        # __Manager = multiprocessing.Manager()
        # _Instances: Dict = __Manager.dict()

        def __new__(_class, *args, **kwargs):
            __current_process = multiprocessing.current_process()
            print(f"[DEBUG] get name: {name} - {__current_process}")
            print(f"[DEBUG] _SingletonClass._Instances: {_SingletonClass._Instances} - {__current_process}")
            if _Instance_Name not in _SingletonClass._Instances.keys():
                print("[DEBUG] it doesn't have this object instance, new one .")
                _SingletonClass._Instances[_Instance_Name] = super(_SingletonClass, _class).__new__(_class, *args, **kwargs)
                _SingletonClass._Instances[_Instance_Name]._sealed = False
            print("[DEBUG] instantiate one finish.")
            return _SingletonClass._Instances[_Instance_Name]


        def __init__(self, *args, **kwargs):
            __current_process = multiprocessing.current_process()
            print(f"[DEBUG] _SingletonClass._Instances at '__init__': {_SingletonClass._Instances} - {__current_process}")
            if _SingletonClass._Instances[_Instance_Name]._sealed:
                print("[DEBUG] instance seal is True.")
                return
            super(_SingletonClass, self).__init__(*args, **kwargs)
            _SingletonClass._Instances[_Instance_Name]._sealed = True

    _SingletonClass.__name__ = _class.__name__
    _SingletonClass.__doc__ = _class.__doc__
    _SingletonClass.__str__ = _class.__str__
    _SingletonClass.__repr__ = _class.__repr__

    return _SingletonClass

