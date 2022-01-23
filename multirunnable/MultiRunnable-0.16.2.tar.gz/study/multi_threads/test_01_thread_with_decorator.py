from threading import Thread
from typing import List, Tuple, Dict, Callable, Union, Any
from functools import wraps
import random
import queue
import time


class TestTask:

    __Function = None
    __Args = ()
    __Kwargs = {}

    @property
    def function(self):
        return self.__Function


    def set_func(self, func):
        self.__Function = func


    @property
    def fun_args(self):
        return self.__Args


    def set_args(self, args):
        self.__Args = args


    @property
    def fun_kwargs(self):
        return self.__Kwargs


    def set_kwargs(self, kwargs):
        self.__Kwargs = kwargs


Result_Queue = queue.Queue()


class Decorator:

    @staticmethod
    def record_result(function: Callable) -> Callable:

        @wraps(function)
        def decorator(self, task: TestTask) -> None:
            self = self
            print(f"inner record_result.args: {task.fun_args}")
            print(f"inner record_result.kwargs: {task.fun_kwargs}")
            value = task.function(*task.fun_args, **task.fun_kwargs)
            self._Threading_Running_Result.append(value)

        return decorator



class MultiThreadingStrategy:

    _Threads_List = []
    _Threading_Running_Result = []

    def __init__(self, worker_num: int):
        self.workers_number = worker_num


    def build_workers(self, function: Callable, *args, **kwargs) -> List[Thread]:
        self._Threads_List = [Thread(target=function, args=args, kwargs=kwargs) for _ in range(self.workers_number)]
        return self._Threads_List


    def build_workers_test(self, function: Callable, args: Tuple = (), kwargs: Dict = {}) -> List[Thread]:
        # # # Task version
        # self._Threads_List = [Thread(target=self.target_task, args=args, kwargs=kwargs) for _ in range(self.workers_number)]

        # # # Function version
        # if args:
        #     args = (function,) + args
        # if kwargs:
        #     args = ()
        #     kwargs["self"] = self
        #     kwargs["function1"] = function

        __task = TestTask()
        __task.set_func(func=function)
        __task.set_args(args=args)
        __task.set_kwargs(kwargs=kwargs)

        __args = ()
        __kwargs = {"task": __task}

        self._Threads_List = [Thread(target=self.target_task, args=__args, kwargs=__kwargs) for _ in range(self.workers_number)]
        return self._Threads_List


    # @staticmethod
    def record_result(function: Callable) -> Callable:

        @wraps(function)
        def decorator(self, task: TestTask) -> None:
            self = self
            print(f"inner record_result.args: {task.fun_args}")
            print(f"inner record_result.kwargs: {task.fun_kwargs}")
            value = task.function(*task.fun_args, **task.fun_kwargs)
            # value = function(*task.fun_args, **task.fun_kwargs)
            print("inner Return value: ", value)
            self._Threading_Running_Result.append(value)

        return decorator


    # @staticmethod
    def record_result_fun(function: Callable) -> Callable:
        """
        Not finish
        :return:
        """

        @wraps(function)
        def decorator(self, function1, *args, **kwargs) -> None:
            self = self
            print(f"inner record_result.args: {args}")
            print(f"inner record_result.kwargs: {kwargs}")
            value = function(*args, **kwargs)
            self._Threading_Running_Result.append(value)

        return decorator


    # @Decorator.record_result
    @record_result
    def target_task(self, task: TestTask) -> None:
        task.function(self, *task.fun_args, **task.fun_kwargs)


    @record_result_fun
    def target_function(self, function1: Callable, *args, **kwargs) -> None:
        """
        Not finish
        :param function1:
        :param args:
        :param kwargs:
        :return:
        """
        function1(self, function1, *args, **kwargs)


    def activate_workers(self, workers_list: List[Thread]) -> None:
        # # Method 1.
        for worker in workers_list:
            self.activate_worker(worker=worker)


    def activate_worker(self, worker: Thread) -> None:
        worker.start()


    def close(self) -> None:
        for threed_index in range(self.workers_number):
            self._Threads_List[threed_index].join()


    def get_result(self) -> List[object]:
        return self._Threading_Running_Result



class TestWorker:

    def __init__(self, worker_num: int):
        self.__strategy = MultiThreadingStrategy(worker_num=worker_num)


    def target_func(self, *args, **kwargs):
        print(f"This is 'target_function'. Parameter is args: {args}")
        print(f"This is 'target_function'. Parameter is kwargs: {kwargs}")
        sleep_time = random.randrange(1, 10)
        print(f"Will sleep for {sleep_time} seconds.")
        time.sleep(sleep_time)
        print("This function wake up.")
        return "Return Value"


    def run(self):
        __args = (1, "this is str")
        __kwargs = {"index1": 1, "index3": "str3"}

        # # # Task version
        # __task = TestTask()
        # __task.set_func(func=self.target_func)
        # __task.set_args(args=__args)
        # __task.set_kwargs(kwargs=__kwargs)
        #
        # __test_kwargs = {"task": __task}
        #
        # # workers_list = self.__strategy.build_workers_test(function=self.target_func, args=__args, kwargs=__kwargs)
        # workers_list = self.__strategy.build_workers_test(function=self.run_task, kwargs=__test_kwargs)

        # # # Function version
        # __args = (self.target_func,) + __args
        # __args = ()
        # __kwargs["function"] = self.target_func
        # workers_list = self.__strategy.build_workers_test(function=self.target_func, args=__args, kwargs=__kwargs)
        workers_list = self.__strategy.build_workers_test(function=self.target_func, args=__args, kwargs=__kwargs)

        self.__strategy.activate_workers(workers_list=workers_list)
        self.__strategy.close()
        result = self.__strategy.get_result()
        print("Final return value is: ", result)


    def run_task(self, task: TestTask) -> List[object]:
        result = task.function(*task.fun_args, **task.fun_kwargs)
        return result


    def run_function(self, function: Callable, *args, **kwargs) -> List[object]:
        result = function(*args, **kwargs)
        return result



if __name__ == '__main__':

    __worker = TestWorker(worker_num=3)
    __worker.run()
