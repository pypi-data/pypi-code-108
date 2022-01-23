from multiprocessing.managers import BaseManager
from multiprocessing import current_process, Manager
from typing import Dict, Any
from os import getpid

from g_manager import assign_to_manager
from test_decorator import sharing_process_new, sharing_process_x



class NamedSingletonMeta(type):

    _Instances: Dict[str, Any] = {}

    def __call__(cls, *args, **kwargs):
        print(f"[DEBUG] Current NamedSingletonABCMeta._Instances: {cls._Instances} - {current_process}::PID: {getpid()}")
        # print(f"[DEBUG] Current NamedSingletonABCMeta._Instances: {_NamedInstances}")
        _cls_name = cls.__name__
        print(f"[DEBUG] NamedSingletonABCMeta:: class name: {_cls_name} - {current_process}::PID: {getpid()}")

        # with PMLock:
        if _cls_name not in cls._Instances:
        # if _cls_name not in _NamedInstances.keys():
            print(f"[DEBUG] NamedSingletonABCMeta:: It doesn't have this instance by the class name '{_cls_name}'. - {current_process}::PID: {getpid()}")
            __super_cls = super(NamedSingletonMeta, cls).__call__(*args, **kwargs)
            cls._Instances[_cls_name] = __super_cls
            # _NamedInstances[_cls_name] = __super_cls
            # _cls_info = {_cls_name: __super_cls}
            # print(f"[DEBUG] _cls_info: {_cls_info}")
            # set_instances(_cls_info)
        else:
            print(f"[DEBUG] NamedSingletonABCMeta:: It already  has this instance by the class name '{_cls_name}'. - {current_process}::PID: {getpid()}")

        # __super_cls = super(NamedSingletonMeta, cls).__call__(*args, **kwargs)
        # cls._Instances[_cls_name] = __super_cls

        print(f"[DEBUG] Now NamedSingletonABCMeta._Instances: {cls._Instances} - {current_process}::PID: {getpid()}")
        # print(f"[DEBUG] Now NamedSingletonABCMeta._Instances: {get_instances()}")
        return cls._Instances[_cls_name]
        # return _NamedInstances[_cls_name]
        # return get_instances_by_key(_cls_name)



class TestA(metaclass=NamedSingletonMeta):

    Cls_Val = 0

    def fun_a(self):
        print(f"This is function a. - PID: {getpid()}")
        print(f"A before Cls_Val: {self.Cls_Val} - {current_process}::PID: {getpid()}")
        self.Cls_Val += 1
        print(f"A after Cls_Val: {self.Cls_Val} - {current_process}::PID: {getpid()}")



class TestB(metaclass=NamedSingletonMeta):

    Cls_Val = 0

    def fun_b(self):
        print(f"***This is function b.*** - {current_process}::PID: {getpid()}")
        print(f"***B before Cls_Val: {self.Cls_Val}*** - {current_process}::PID: {getpid()}")
        self.Cls_Val += 1
        print(f"***B after Cls_Val: {self.Cls_Val}*** - {current_process}::PID: {getpid()}")


# @sharing_process_new
@sharing_process_x
class TestAWithDecorator(metaclass=NamedSingletonMeta):

    Cls_Val = 0

    def __init__(self, param=None, nested_cls=None):
        self._param = param
        if type(self._param) is int:
            self.Cls_Val = param

        self._nested_cls = nested_cls


    def fun_a(self):
        print(f"This is function a. - {current_process}:: PID: {getpid()}")
        print(f"self._param:{self._param} - {current_process}:: PID: {getpid()}")
        print(f"A before Cls_Val: {self.Cls_Val} - {current_process}::PID: {getpid()}")
        self.Cls_Val += 1
        print(f"A after Cls_Val: {self.Cls_Val} - {current_process}::PID: {getpid()}")
        print(f"The nested class: {self._nested_cls}")
        print(f"The dir of nested class: {dir(self._nested_cls)}")
        print(f"The var of nested class: {vars(self._nested_cls)}")
        print(f"[DEBUG] running function 'fun_b' via self._nested_cls")
        self._nested_cls.fun_b()
        # print(f"The Cls_Val of B class is: {self._nested_cls.cls_val} - {current_process}::PID: {getpid()}")


# @sharing_process_new
@sharing_process_x
class TestBWithDecorator(metaclass=NamedSingletonMeta):

    Cls_Val = 0

    # def __init__(self):
    #     self.Cls_Val = 0

    def get_cls_val(self):
        return self.Cls_Val

    def set_cls_val(self, value):
        self.Cls_Val = value

    def fun_b(self):
        print(f"***This is function b.*** - {current_process}::PID: {getpid()}")
        print(f"***B before Cls_Val: {self.Cls_Val}*** - {current_process}::PID: {getpid()}")
        self.Cls_Val += 1
        print(f"***B after Cls_Val: {self.Cls_Val}*** - {current_process}::PID: {getpid()}")


