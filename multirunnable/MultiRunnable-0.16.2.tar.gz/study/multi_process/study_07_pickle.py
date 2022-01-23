from abc import ABCMeta, abstractmethod
from functools import wraps
from multiprocessing import Process, Pool
import random
import time



class TestDecorator:

    @classmethod
    def decorator(cls, function):
        print("This is decorator.")

        @wraps(function)
        def _(*args, **kwargs):
            value = function(*args, **kwargs)
            return value

        return _




class TargetExample:

    def func(self):
        print("This is general function.")
        random_sleep_time = random.randrange(1, 10)
        print(f"It will sleep for {random_sleep_time} seconds ...")
        time.sleep(random_sleep_time)


    @classmethod
    def cls_func(cls):
        print("This is classmethod function.")
        random_sleep_time = random.randrange(1, 10)
        print(f"It will sleep for {random_sleep_time} seconds ...")
        time.sleep(random_sleep_time)


    @staticmethod
    def stc_func():
        print("This is staticmethod function.")
        random_sleep_time = random.randrange(1, 10)
        print(f"It will sleep for {random_sleep_time} seconds ...")
        time.sleep(random_sleep_time)


    def decorator_func(self):
        print("This is general function decorate with a Python decorator.")
        random_sleep_time = random.randrange(1, 10)
        print(f"It will sleep for {random_sleep_time} seconds ...")
        time.sleep(random_sleep_time)



class ProcessClient:

    def run_general_func(self):
        p = Process(target=TargetExample().func)
        p.run()
        # p.close()
        # p.join()


    def run_general_cls_func(self):
        p = Process(target=TargetExample.cls_func)
        p.run()
        # p.join()
        # p.close()


    def run_general_stc_func(self):
        p = Process(target=TargetExample.stc_func)
        p.run()
        # p.join()
        # p.close()


    def run_general_func_with_decorator(self, target, *args, **kwargs):
        p = self._generate_process(target=target, args=args, kwargs=kwargs)
        p.run()


    def _generate_process(self, target, args, kwargs):

        @wraps(target)
        @TestDecorator.decorator
        def inner_func(*_args, **_kwargs):
            print("This is inner function.")
            target(*_args, **_kwargs)

        print("[CHECK] target: ", target)
        print("[CHECK] inner_func: ", inner_func)
        return Process(target=inner_func, args=args, kwargs=kwargs)



class PoolClient:

    def run_general_func(self):
        with Pool(processes=3) as pool:
            pa = pool.apply_async(TargetExample().func)
            pa.get()


    def run_general_cls_func(self):
        with Pool(processes=3) as pool:
            pa = pool.apply_async(TargetExample.cls_func)
            pa.get()


    def run_general_stc_func(self):
        with Pool(processes=3) as pool:
            pa = pool.apply_async(TargetExample.stc_func)
            pa.get()


    def run_general_func_with_decorator(self):
        with Pool(processes=3) as pool:
            pa = pool.apply_async(TargetExample.decorator_func)
            pa.get()



if __name__ == '__main__':

    pc = ProcessClient()
    # pc = PoolClient()

    # pc.run_general_func()    # Run OK
    # pc.run_general_cls_func()    # Run OK
    # pc.run_general_stc_func()    # Run OK
    pc.run_general_func_with_decorator(TargetExample().func)
