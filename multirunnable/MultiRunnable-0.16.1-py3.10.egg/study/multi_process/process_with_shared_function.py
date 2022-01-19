from task import SharedTask
from decorator import SharedFunc

from typing import Callable, Any
from multiprocessing import Pool
from functools import wraps



# class BaseTaskFunction:
#
#     @classmethod
#     def function(cls, *args, **kwargs):
#         print("[NaN] This is function, will do nothing.")
#         pass
#
#
#     @classmethod
#     def initialization(cls, *args, **kwargs) -> None:
#         print("[NaN] This is initialization, will do nothing.")
#         pass
#
#
#     @classmethod
#     def done_handler(cls, result):
#         print("[NaN] This is done-handler, will do nothing.")
#         return result
#
#
#     @classmethod
#     def error_handler(cls, e: Exception):
#         print("[NaN] This is error-handler, will do nothing.")
#         return e
#
#
#
# class SharedTask:
#
#     __Function = None
#     __Func_Args = None
#     __Func_Kwargs = None
#     __Initialization = None
#     __Done_Handler = None
#     __Error_Handler = None
#
#     def __init__(self):
#         self.__Initialization = BaseTaskFunction.initialization
#         self.__Done_Handler = BaseTaskFunction.done_handler
#         self.__Error_Handler = BaseTaskFunction.error_handler
#
#
#     @property
#     def function(self):
#         return self.__Function
#
#
#     def set_func(self, func):
#         self.__Function = func
#
#
#     @property
#     def func_args(self):
#         return self.__Func_Args
#
#
#     def set_func_args(self, args):
#         self.__Func_Args = args
#
#
#     @property
#     def initialization(self):
#         return self.__Initialization
#
#
#     @property
#     def func_kwargs(self):
#         return self.__Func_Kwargs
#
#
#     def set_func_kwargs(self, kwargs):
#         self.__Func_Kwargs = kwargs
#
#
#     @property
#     def done_handler(self):
#         return self.__Done_Handler
#
#
#     @property
#     def error_handler(self):
#         return self.__Error_Handler
#
#
#
# class SharedFunc:
#
#     def try_decorator(function: Callable):
#
#         @wraps(function)
#         def try_catch_code(*args, **kwargs) -> Any:
#             try:
#                 result = function(*args, **kwargs)
#             except Exception as e:
#                 print(e)
#                 return e
#             else:
#                 print("Done function.")
#                 return result
#
#         return try_catch_code
#
#
#     def try_task_decorator(function: Callable):
#
#         @wraps(function)
#         def try_catch_code(self, task: SharedTask) -> Any:
#             try:
#                 result = task.function(*task.func_args, **task.func_kwargs)
#             except Exception as e:
#                 result = task.error_handler(e=e)
#                 print("Catch the exception in task.")
#                 print(e)
#                 return result
#             else:
#                 result = task.done_handler(result=result)
#                 print("Done function.")
#                 return result
#
#         return try_catch_code
#
#
#     @classmethod
#     def try_catch_mechanism(cls, function: Callable, *args, **kwargs) -> Any:
#         try:
#             result = function(*args, **kwargs)
#         except Exception as e:
#             print(e)
#             return e
#         else:
#             print("Done function.")
#             return result



class SharedFuncClient:

    Process_Number = 0

    def __init__(self, worker_num: int):
        self.Process_Number = worker_num


    def target_func(self, *args, **kwargs) -> str:
        print("This is target running function in process.")
        print("This is target function args: ", args)
        print("This is target function kwargs: ", kwargs)
        # raise Exception("Test for error")
        return "You are 87."


    def target_func_adapter(self, *args, **kwargs):
        print("This is function adapter.")
        SharedFunc.try_catch_mechanism(function=self.target_func, *args, **kwargs)


    @SharedFunc.try_decorator
    def target_func_with_decorator(self, *args, **kwargs) -> str:
        print("This is target running function in process.")
        print("This is target function args: ", args)
        print("This is target function kwargs: ", kwargs)
        return "You are 87."


    @SharedFunc.try_task_decorator
    def target_task_with_decorator(self, task: SharedTask) -> str:
        print("This is target_task_with_decorator function in process.")
        # print("This is target function task: ", task)
        # return "You are 87 task."
        return task.function(*task.func_args, **task.func_kwargs)


    def process_with_target(self) -> None:
        __pool = Pool(processes=self.Process_Number)
        __fun_args = (1, "this is args")
        __fun_kwargs = {"param1": 1, "param2": "this is kwargs"}
        __process = __pool.apply_async(func=self.target_func, *__fun_args, **__fun_kwargs)
        result = __process.get()
        successful = __process.successful()
        print("Function successful: ", successful)
        print("Function result: ", result)


    def process_with_inner_target(self) -> None:
        __pool = Pool(processes=self.Process_Number)
        # __fun_args = (self.target_func, 1, "this is args")
        __fun_args = ()
        __fun_kwargs = {"function": self.target_func, "param1": 1, "param2": "this is kwargs"}

        global Mechanism
        Mechanism = SharedFunc.try_catch_mechanism

        # __process = __pool.apply_async(func=SharedFunc.try_catch_mechanism, *__fun_args, **__fun_kwargs)
        __process = __pool.apply_async(func=Mechanism, args=__fun_args, kwds=__fun_kwargs)
        result = __process.get()
        successful = __process.successful()
        print("Function successful: ", successful)
        print("Function result: ", result)


    def process_with_adapter_target(self) -> None:
        __pool = Pool(processes=self.Process_Number)
        # __fun_args = (self.target_func, 1, "this is args")
        __fun_args = ()
        __fun_kwargs = {"param1": 1, "param2": "this is kwargs"}

        __process_pool = []
        for _ in range(self.Process_Number):
            __process = __pool.apply_async(func=self.target_func_adapter, args=__fun_args, kwds=__fun_kwargs)

        for __process in __process_pool:
            result = __process.get()
            successful = __process.successful()
            print("Function successful: ", successful)
            print("Function result: ", result)

        __pool.close()


    def process_with_decorated_target(self) -> None:
        __pool = Pool(processes=self.Process_Number)
        # __fun_args = (1, "this is args")
        __fun_args = ()
        __fun_kwargs = {"param1": 1, "param2": "this is kwargs"}

        # global Decorator_Func
        # Decorator_Func = self.target_func_with_decorator

        # # For debug
        # result = Decorator_Func(*__fun_args, **__fun_kwargs)
        # print("Function result: ", result)

        __process_pool = []
        for _ in range(self.Process_Number):
            # __process = __pool.apply_async(func=self.target_func_with_decorator, *__fun_args, **__fun_kwargs)
            __process = __pool.apply_async(func=self.target_func_with_decorator, args=__fun_args, kwds=__fun_kwargs)
            # __process = __pool.apply_async(func=Decorator_Func, args=__fun_args, kwds=__fun_kwargs)
            __process_pool.append(__process)

        for __process in __process_pool:
            result = __process.get()
            successful = __process.successful()
            print("Function successful: ", successful)
            print("Function result: ", result)

        __pool.close()


    def process_with_decorated_task(self) -> None:

        __task = SharedTask()
        __task.set_func(func=self.target_func)
        __task.set_func_args(args=())
        __task.set_func_kwargs(kwargs={"param1": 1, "param2": "this is kwargs"})

        __pool = Pool(processes=self.Process_Number)

        # __process_pool = []
        # for _ in range(self.Process_Number):
        #     # __process = __pool.apply_async(func=self.target_func_with_decorator, *__fun_args, **__fun_kwargs)
        #     __process = __pool.apply_async(
        #         func=self.target_task_with_decorator,
        #         args=(), kwds={"task": __task},
        #         callback=None, error_callback=None)
        #     # __process = __pool.apply_async(func=Decorator_Func, args=__fun_args, kwds=__fun_kwargs)
        #     __process_pool.append(__process)

        # for __process in __process_pool:
        #     result = __process.get()
        #     successful = __process.successful()
        #     print("Function successful: ", successful)
        #     print("Function result: ", result)

        __process = __pool.map_async(
            self.target_task_with_decorator,
            [__task, __task]
        )

        __pool.starmap_async()

        # __process = __pool.starmap_async(
        #     self.target_task_with_decorator,
        #     [(__task, )]
        # )

        print("Function result: ", __process.get())

        __pool.close()
        __pool.join()



if __name__ == '__main__':

    __shared_client = SharedFuncClient(worker_num=1)
    # __shared.process_with_target()
    # __shared_client.process_with_inner_target()
    # __shared_client.process_with_adapter_target()
    # __shared_client.process_with_decorated_target()
    __shared_client.process_with_decorated_task()
