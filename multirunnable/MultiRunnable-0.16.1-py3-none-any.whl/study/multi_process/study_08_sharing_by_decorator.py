from multiprocessing import Process, Manager
from multiprocessing.managers import Namespace



def Sharing_In_Processes(_class):
    _cls_name = _class.__name__
    print(f"_class: {_class}")
    print(f"_cls_name: {_cls_name}")
    setattr(Global_Namespace, _cls_name, _class)
    return getattr(Global_Namespace, _cls_name)



@Sharing_In_Processes
class A:

    def fun_a(self):
        print("This is function a.")



@Sharing_In_Processes
class B:

    def fun_b(self):
        print("This is function b.")



class RunCls:

    @classmethod
    def run(cls, a: A, b: B):
        print(f"a instance ID: {id(a)}")
        print(f"b instance ID: {id(b)}")
        a.fun_a()
        b.fun_b()



if __name__ == '__main__':

    Global_Manager = Manager()
    Global_Namespace = Global_Manager.Namespace()

    _a = A()
    _b = B()

    print("Initial process ...")
    processes = [Process(target=RunCls.run, args=(_a, _b)) for _ in range(3)]

    print("Run process ")
    for _p in processes:
        _p.run()

    print("End process ")
    for _p in processes:
        _p.close()
        _p.join()

