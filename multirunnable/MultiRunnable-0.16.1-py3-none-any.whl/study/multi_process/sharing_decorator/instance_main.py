from g import get_process_namespace, set_process_namespace, chk_process_namespace, PLock

import abc
from abc import ABCMeta
from typing import Dict, Any
import multiprocessing as mp

PM = mp.Manager()
PNS = PM.Namespace()
_PNS_Instances = PM.Namespace()

_Instances = {}


class NamedSingletonABCMeta(ABCMeta):

    def __call__(cls, *args, **kwargs):
        # global _PNS_Instances
        _cls_name = cls.__name__
        from g import PNS
        print(f"[DEBUG] Current NamedSingletonABCMeta._Instances: {PNS}")
        print(f"[DEBUG] NamedSingletonABCMeta:: class name: {_cls_name}")
        with PLock:
            if chk_process_namespace(_cls_name) is False:
            # if _cls_name not in _Instances:
                print(f"[DEBUG] NamedSingletonABCMeta:: It doesn't have this instance by the class name '{_cls_name}'.")
                __super_cls = super(NamedSingletonABCMeta, cls).__call__(*args, **kwargs)
                print(f"Start to save instance into Namespace ...")
                set_process_namespace(_cls_name, __super_cls)
                # setattr(_PNS_Instances, _cls_name, __super_cls)
                print(f"Save finish and get it.")
                # cls._Instances[_cls_name] = __common_cls
                # _Instances[_cls_name] = __super_cls
            # _instance = getattr(_PNS_Instances, _cls_name)
            _instance = get_process_namespace(_cls_name)
            print(f"[DEBUG] Now NamedSingletonABCMeta._Instances: {_instance}")
            return _instance


class A(metaclass=NamedSingletonABCMeta):

    @abc.abstractmethod
    def test_fun(self):
        pass



class AImpl(A):

    def test_fun(self):
        print(f"This is testing function.")



class TestCls:

    def test_fun(self):
        _a_impl = AImpl()
        _a_impl.test_fun()


# main_run()
#
#
# if __name__ == '__main__':
#
#     _a_impl = AImpl()
#
#     processes = [mp.Process(target=_a_impl.test_fun) for _ in range(3)]
#
#     print("Run process ")
#     for _p in processes:
#         # _p.run()
#         _p.start()
#
#     print("End process ")
#     for _p in processes:
#         _p.join()
#         _p.close()
