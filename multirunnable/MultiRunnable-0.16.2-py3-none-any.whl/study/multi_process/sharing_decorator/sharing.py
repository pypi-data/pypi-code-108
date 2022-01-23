from multiprocessing import Process, Manager
from multiprocessing.managers import Namespace


Global_Manager = Manager()
Global_Namespace = Global_Manager.Namespace()


def Sharing_In_Processes(_class):
    _cls_name = str(_class.__name__)
    print(f"_class: {_class}")
    print(f"_cls_name: {_cls_name}")
    setattr(Global_Namespace, _cls_name, _class)
    return getattr(Global_Namespace, _cls_name)

