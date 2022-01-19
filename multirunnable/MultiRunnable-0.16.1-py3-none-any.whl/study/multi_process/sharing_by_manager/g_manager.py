from multiprocessing import Lock
from typing import Dict, Any
from os import getpid

from multiprocessing import managers
# import multiprocessing


# Backup original AutoProxy function
backup_autoproxy = managers.AutoProxy


# Defining a new AutoProxy that handles unwanted key argument 'manager_owned'
def redefined_autoproxy(token, serializer, manager=None, authkey=None,
          exposed=None, incref=True, manager_owned=True):
    # Calling original AutoProxy without the unwanted key argument
    print(f"[DEBUG] coming the new annotation 'AutoProxy'.")
    return backup_autoproxy(token, serializer, manager, authkey,
                     exposed, incref)


# Updating AutoProxy definition in multiprocessing.managers package
managers.AutoProxy = redefined_autoproxy


_Assign_Manager_Flag: Dict[str, bool] = {}
_Manager_Start_Flag = False
GM = None
PMLock = Lock()


class GManager(managers.BaseManager):
    pass


def get_current_manager() -> managers.BaseManager:
    return GM


# a base class with the methods generated for us. The second argument
# doubles as the 'permitted' names, stored as _exposed_
TestBWithDecoratorBaseProxy = managers.MakeProxyType(
    "TestBWithDecoratorBaseProxy",
    ("__getattribute__", "get_cls_val", "set_cls_val", "fun_b"),
)


class TestBWithDecoratorProxy(TestBWithDecoratorBaseProxy):

    Cls_Val = 0

    def get_cls_val(self):
        print(f"[DEBUG] go into Proxy object *get_cls_val*.")
        return self._callmethod('get_cls_val')

    def set_cls_val(self, value):
        print(f"[DEBUG] go into Proxy object *set_cls_val*.")
        return self._callmethod('set_cls_val', (value,))

    def fun_b(self, *args, **kwargs):
        print(f"[DEBUG] go into Proxy object *fun_b*.")
        return self._callmethod("fun_b", args, kwargs)


def assign_to_manager(target_cls):
    _cls_name = target_cls.__name__
    with PMLock:
        global _Assign_Manager_Flag
        if _cls_name in _Assign_Manager_Flag.keys():
            print(f"[DEBUG] cls: {_cls_name} in _Assign_Manager_Flag.")
            if _Assign_Manager_Flag[_cls_name] is False:
                print(f"[DEBUG] class name: {_cls_name}")
                print(f"[DEBUG] class object: {target_cls}")

                # # # # Version 1. -
                # When use nested manager sub-class instance, got exception about:
                # TypeError: AutoProxy() got an unexpected keyword argument 'manager_owned'
                # GManager.register(str(_cls_name), target_cls)

                # # # # Version 2.
                if _cls_name == "TestAWithDecorator":
                    GManager.register(typeid=str(_cls_name), callable=target_cls)
                else:
                    GManager.register(typeid=str(_cls_name), callable=target_cls, proxytype=TestBWithDecoratorBaseProxy)

                _Assign_Manager_Flag[_cls_name] = True
            else:
                print(f"[DEBUG] cls {_cls_name} has been already.")
        else:
            print(f"[DEBUG] cls: {_cls_name} not in _Assign_Manager_Flag.")
            print(f"[DEBUG] class name: {_cls_name}")
            print(f"[DEBUG] class object: {target_cls}")
            GManager.register(str(_cls_name), target_cls)
            _Assign_Manager_Flag[_cls_name] = True


def get_manager_attr(attr):
    # _current_manager = get_current_manager()
    if GM is None:
    # if _current_manager is None:
        raise ValueError("Object _SharingManager not be initialed yet.")

    print(f"[CHECK] attr: {attr}")
    # print(f"[CHECK] dir: {dir(GM)}")
    # print(f"[CHECK] vars: {vars(GM)}")
    # if hasattr(_current_manager, attr):
    if attr not in dir(GM):
        raise AttributeError("Target attribute doesn't exist.")

    _attr = getattr(GM, attr)
    print(f"[INFO] _attr: {_attr}")
    return _attr


def GlobalManager():
    global _Manager_Start_Flag, GM
    with PMLock:
        print(f"[DEBUG] before running _Manager_Start_Flag: {_Manager_Start_Flag}")
        print(f"[DEBUG] _Manager_Start_Flag is False: {_Manager_Start_Flag is False}")
        if _Manager_Start_Flag is False:
            GM = GManager()
            print(f"[DEBUG] Try to start multiprocessing.Manager ...")
            GM.start()
            _Manager_Start_Flag = True
            print(f"[DEBUG] after running _Manager_Start_Flag: {_Manager_Start_Flag}")
            print(f"[DEBUG] Start multiprocessing.Manager successfully.")
        else:
            print(f"[DEBUG] multiprocessing.Manager has already.")

        return GM


