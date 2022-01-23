from multirunnable._singletons import (
    NamedSingletonABCMeta)
from multirunnable.test.interface import MarkerCls

from abc import abstractmethod
from multiprocessing import Manager


# @Sharing_In_Processes
# @simple_singleton
# @singleton
# @namedsingleton
# class ACls:
# class ACls(Singleton):
# class ACls(ConnectionPoolSingleton):
# class ACls(metaclass=SingletonMeta):
# class ACls(metaclass=NamedSingletonMeta):
# class ACls(metaclass=ConnectionPoolSingletonMeta):
# class ACls(metaclass=NamedSingletonABCMeta):
class ACls(MarkerCls):

    # Cls_Val = 0
    Cls_Val = Manager().Value(int, 0)

    def __init__(self):
        pass


    @abstractmethod
    def fun_a(self):
        pass



class AACls(ACls):

    def fun_a(self):
        print("This is function a.")
        print(f"ACls before Cls_Val: {self.Cls_Val}")
        self.Cls_Val += 1
        print(f"ACls after Cls_Val: {self.Cls_Val}")



class AADBCls(ACls):

    def fun_a(self):
        print("This is function a.")
        print(f"ACls before Cls_Val: {self.Cls_Val}")
        self.Cls_Val += 1
        print(f"ACls after Cls_Val: {self.Cls_Val}")


# @Sharing_In_Processes
# @simple_singleton
# @namedsingleton(name="test_b_class")
# class B:
# class B(Singleton):
# class B(metaclass=NamedSingletonMeta):
class B(metaclass=NamedSingletonABCMeta):

    Cls_Val = 0

    def fun_b(self):
        print("This is function b.")
        print(f"B before Cls_Val: {self.Cls_Val}")
        self.Cls_Val += 1
        print(f"B after Cls_Val: {self.Cls_Val}")



class AClsNo:

    def fun_a(self):
        print("This is function a.")



class BNo:

    def fun_b(self):
        print("This is function b.")


