"""
Note:
    Currently, all of the examples for concurrent or coroutine, not for parallel.
"""
from multirunnable.parallel.shared import get_manager, get_namespace, set_singletons, get_singletons, get_singletons_by_key

# from global_var import get_manager

from typing import Dict
from functools import wraps, update_wrapper
import multiprocessing
import threading
import inspect
import random
import time
import sys


# Process_Manager = multiprocessing.Manager()


def simple_singleton(_class):

    __Instances = {}

    def get_instance(*args, **kwargs):
        if _class not in __Instances.keys():
            __Instances[_class] = _class(*args, **kwargs)
        return __Instances[_class]

    return get_instance




class Singleton:

    # # # # Method 1. For concurrent and coroutine,
    _Instances = {}
    # # # # Method 2. For parallel.
    # _Instances = multiprocessing.Manager().dict()

    def __new__(cls, *args, **kwargs):
        if cls not in cls._Instances.keys():
            cls._Instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._Instances[cls]


# Process_Lock = Process_Manager.Lock()
# Process_Semaphore = Process_Manager.BoundedSemaphore(value=3)


_Instance = None
_Instances = None


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

    # # # # Method 1. For concurrent and coroutine.
    # # # # For example in Python library.
    # # # # Concurrent -> threading
    # # # # Coroutine -> greenlet, gevent
    # _Instances: Dict = {}
    # _Ins_Lock = threading.Lock()

    # # # # Method 2. For parallel.
    # # # # Parallel -> multiprocessing
    # __Manager = multiprocessing.Manager()
    __Manager = get_manager()
    # _Namespace = __Manager.Namespace()
    _Namespace = get_namespace()
    _Ins_Lock = __Manager.Lock()
    # _Instance = None

    def __call__(cls, *args, **kwargs):
        # global _Instance
        print(f"In __call__ before Lock - {multiprocessing.current_process()}")
        with cls._Ins_Lock:
            print(f"In __call__ after Lock - {multiprocessing.current_process()}")
            _instances_dict = cls.get_singleton()
            print(f"[DEBUG] _instances_dict: {_instances_dict} - {multiprocessing.current_process()}")
            if _instances_dict is None or (_instances_dict is not None and cls.__name__ not in _instances_dict.keys()):
                print(f"[DEBUG] no instance. - {multiprocessing.current_process()}")
                __super_cls = super(SingletonMeta, cls).__call__(*args, **kwargs)
                print(f"[DEBUG] __super_cls: {__super_cls} - {multiprocessing.current_process()}")
                set_singletons(name=cls.__name__, cls=__super_cls)
                # _instances_dict[cls.__name__] = __super_cls
                print(f"[DEBUG] saving finish")
            else:
                print(f"[DEBUG] has instance and return back directly. - {multiprocessing.current_process()}")
        target_instance = get_singletons_by_key(key=cls.__name__)
        cls_id = id(target_instance)
        print(f"[DEBUG] instance ID: {id(cls_id)} - {multiprocessing.current_process()}")
        return target_instance


    @classmethod
    def get_singleton(cls) -> Dict:
        from multirunnable.parallel.shared import get_manager, get_singletons
        from multirunnable.parallel._shared_var import Globalize

        _singletons = get_singletons()
        if _singletons is None:
            manager = get_manager()
            _singletons = manager.dict()
            Globalize.singletons(singletons=_singletons)

        return _singletons


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
        Resolve issue. It doesn't work anymore because instanciate multiprocessing.Manager much times .
        It needs to instanciate multiprocessing.Manager first and ONCE before we use the relateed features
        like Namespace, dict, Lock or something else.
    """

    # # # # Method 1. For concurrent and coroutine.
    # # # # For example in Python library.
    # # # # Concurrent -> threading
    # # # # Coroutine -> greenlet, gevent
    # _Instances: Dict = {}
    # _Ins_Lock = threading.Lock()

    # # # # Method 2. For parallel.
    # # # # Parallel -> multiprocessing
    # __Manager = multiprocessing.Manager()
    __Manager = get_manager()
    # _Namespace = __Manager.Namespace()
    _Namespace = get_namespace()
    _Ins_Lock = __Manager.Lock()
    _Instances = __Manager.dict()

    def __call__(cls, *args, **kwargs):
        # print(f"[DEBUG] process lock acquired.")
        # print(f"In __call__ before Lock, Lock Status: {cls._Ins_Lock.locked} - {multiprocessing.current_process()}")
        print(f"In __call__ before Lock - {multiprocessing.current_process()}")
        with cls._Ins_Lock:
            # print(f"In __call__ after Lock, Lock Status: {cls._Ins_Lock.locked} - {multiprocessing.current_process()}")
            print(f"In __call__ after Lock - {multiprocessing.current_process()}")
            print(f"[DEBUG] cls._Instances: {cls._Instances} - {multiprocessing.current_process()}")
            if cls.__name__ not in cls._Instances.keys():
                print(f"[DEBUG] no instance. - {multiprocessing.current_process()}")
                print(f"[DEBUG] cls: {cls.__name__} - {multiprocessing.current_process()}")
                __super_cls = super(NamedSingletonMeta, cls).__call__(*args, **kwargs)
                print(f"[DEBUG] __super_cls: {__super_cls} - {multiprocessing.current_process()}")
                # # # # Threading
                # cls._Instances[str(cls.__name__)] = __super_cls
                # # # # Multiprocessing
                # setattr(cls._Namespace, cls.__name__, __super_cls)
                # cls._Instances[str(cls.__name__)] = getattr(cls._Namespace, cls.__name__)
                # # # # New feature of multirunnable
                set_singletons(name=str(cls.__name__), cls=__super_cls)
                print(f"[DEBUG] saving finish")
            else:
                print(f"[DEBUG] has instance and return back directly. - {multiprocessing.current_process()}")
            print(f"[DEBUG] _Instances: {get_singletons()} - {multiprocessing.current_process()}")
            # print(f"[DEBUG] instance ID: {id(cls._Instances[cls.__name__])} - {multiprocessing.current_process()}")
            # return cls._Instances[cls]
        # cls_id = id(cls._Instances[cls.__name__])
        cls_id = id(get_singletons_by_key(cls.__name__))
        print(f"[DEBUG] cls_id: {cls_id}")
        # return cls._Instances[cls.__name__]
        return get_singletons_by_key(key=cls.__name__)



def singleton(_class):

    if inspect.isclass(_class) is False:
        raise ValueError("The target object be decorated should be a 'class' type object.")

    class _SingletonClass(_class):

        _Instance = None

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
        _NamedSingleton(_class=cls, name=name)
    else:
        @wraps(cls)
        def _(cls):
            return _NamedSingleton(_class=cls, name=name)
        return _



class test_cls_wrapper:
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}
        update_wrapper(self, func)  ## TA-DA! ##


    def __call__(self, *args, **kwargs):
        return self



def _NamedSingleton(_class, name: str):

    if inspect.isclass(_class) is False:
        raise ValueError("The target object be decorated should be a 'class' type object.")

    if name is None:
        raise ValueError("Option *name* could not be None value.")
    _Instance_Name = name

    # @test_cls_wrapper(_class)
    class _SingletonClass(_class):

        _Instances: Dict = {}
        # __Manager = multiprocessing.Manager()
        # _Instances: Dict = __Manager.dict()

        def __new__(_class, *args, **kwargs):
            __current_process = multiprocessing.current_process()
            print(f"[DEBUG] get name: {name} - {__current_process}")
            print(f"[DEBUG] _SingletonClass._Instances: {_SingletonClass._Instances} - {__current_process}")
            if _Instance_Name not in _SingletonClass._Instances.keys():
                _SingletonClass._Instances[_Instance_Name] = super(_SingletonClass, _class).__new__(_class, *args, **kwargs)
                _SingletonClass._Instances[_Instance_Name]._sealed = False
            return _SingletonClass._Instances[_Instance_Name]


        def __init__(self, *args, **kwargs):
            __current_process = multiprocessing.current_process()
            print(f"[DEBUG] _SingletonClass._Instances at '__init__': {_SingletonClass._Instances} - {__current_process}")
            if _SingletonClass._Instances[_Instance_Name]._sealed:
                return
            super(_SingletonClass, self).__init__(*args, **kwargs)
            _SingletonClass._Instances[_Instance_Name]._sealed = True

    _SingletonClass.__name__ = _class.__name__
    _SingletonClass.__doc__ = _class.__doc__
    _SingletonClass.__str__ = _class.__str__
    _SingletonClass.__repr__ = _class.__repr__

    return _SingletonClass

