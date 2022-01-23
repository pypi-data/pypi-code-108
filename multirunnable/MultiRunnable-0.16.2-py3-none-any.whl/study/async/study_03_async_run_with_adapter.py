from typing import List, Callable
from types import FunctionType, MethodType
from multipledispatch import dispatch
from asyncio import Task
from collections import Iterable
import asyncio
import random
import time


async def fun_1(param, index):
    print("This is function_1.")
    print(f"Parameter: {param}")
    sleep_time = random.randrange(1, 10)
    print(f"Func_1 Will sleep for {sleep_time} seconds ... - Async-{index}")
    await asyncio.sleep(sleep_time)
    print(f"Func_1 end, time: {time.time()}")
    return "This is fun_1"


async def fun_2(param, index):
    print("This is function_2.")
    print(f"Parameter: {param}")
    sleep_time = random.randrange(1, 10)
    print(f"Func_2 Will sleep for {sleep_time} seconds ... - Async-{index}")
    await asyncio.sleep(sleep_time)
    print(f"Func_2 end, time: {time.time()}")
    return "This is fun_2"



async def run_fun():
    value = await asyncio.gather(fun_1(param="test_1", index="1"), fun_2(param="test_2", index="2"))
    print("value: ", value)



def asyncio_gather():
    asyncio.run(run_fun())
    # asyncio.run(run_fun())    # Will be blocking run



async def __async_task_1():
    _task_1 = asyncio.create_task(fun_1(param="test_1", index="1"))

    # _task_1_name = _task_1.get_name()
    # _task_1_loop = _task_1.get_loop()
    # _task_1_result = _task_1.result()
    # _task_1_exception = _task_1.exception()
    # _task_1_coro = _task_1.get_coro()
    # _task_1_stack = _task_1.get_stack()
    value = await _task_1

    print("Task_1: ", value)
    # print("Task_1_Name: ", _task_1_name)
    # print("Task_1_Loop: ", _task_1_loop)
    # print("Task_1_Result: ", _task_1_result)
    # print("Task_1_Exception: ", _task_1_exception)
    # print("Task_1_Coro: ", _task_1_coro)
    # print("Task_1_Stack: ", _task_1_stack)



async def __async_task_2():
    _task_2 = asyncio.create_task(fun_2(param="test_2", index="2"))
    value = await _task_2
    print("Task_2: ", value)



async def __async_task_3():
    _task_1 = asyncio.create_task(fun_1(param="test_1", index="1"))
    _task_2 = asyncio.create_task(fun_2(param="test_2", index="2"))

    value_1 = await _task_1
    value_2 = await _task_2

    print("Task_1: ", value_1)
    print("Task_2: ", value_2)



async def __async_task_3_new():
    # # # # Generate a list which saving async tasks
    # _async_tasks = create_async_task(fun_1, **{"param": "new_test_1", "index": "new_1"})

    _fun_kwargs = {"param": "new_test_1", "index": "new_1"}
    _async_tasks = [create_one_async_task(fun_1, **_fun_kwargs) for _ in range(5)]

    # # # # Will occur error:
    # routine object activate_task at 0x10a3283c8>, <coroutine object activate_task at 0x10a328448>, <coroutine object activate_task at 0x10a3284c8>]
    # ./apache-pyocean/study/async/study_03_async_run_with_adapter.py:83: RuntimeWarning: coroutine 'activate_task' was never awaited
    #   print("Tasks Result: ", list(values_iter))
    # RuntimeWarning: Enable tracemalloc to get the object allocation traceback
    # values_iter = map(activate_task, _async_tasks)

    values = [await task for task in _async_tasks]
    print("Tasks Result: ", values)



def __async_task_3_newer():

    async def _target():
        _fun_kwargs = {"param": "new_test_1", "index": "new_1"}
        _async_tasks = [create_one_async_task(fun_1, **_fun_kwargs) for _ in range(5)]
        values = [await task for task in _async_tasks]
        print("Tasks Result: ", values)

    asyncio.run(_target())


def create_one_async_task(function, *args, **kwargs):
    return asyncio.create_task(function(*args, **kwargs))


async def create_async_task(function, *args, **kwargs):
    return [asyncio.create_task(function(*args, **kwargs)) for _ in range(5)]


async def activate_task(task):
    # return await task
    value = await task
    return value



def asyncio_run():
    asyncio.run(__async_task_3_new())
    # asyncio.run(__async_task_1())
    # asyncio.run(__async_task_2())    # Will be blocking run



class AsyncOpt:

    """
    2 strategy: asyncio.run or asyncio.event_loop
    """

    __Running_Time = 0
    _Async_Running_Result = []

    executors_number = 3

    def run(self, function, args=None) -> None:

        async def __run_process():
            workers_list = [self._generate_worker(function, args) for _ in range(self.executors_number)]
            print("[DEBUG] workers_list: ", workers_list)
            await self.activate_workers(workers_list)

        asyncio.run(__run_process())


    @dispatch((FunctionType, MethodType), tuple)
    def _generate_worker(self, function: Callable, args):
        __worker = self.generate_worker(function, *args)
        return __worker


    @dispatch((FunctionType, MethodType), dict)
    def _generate_worker(self, function: Callable, args):
        __worker = self.generate_worker(function, **args)
        return __worker


    def generate_worker(self, target: Callable, *args, **kwargs) -> Task:
        return asyncio.create_task(target(*args, **kwargs))


    @dispatch(Task)
    async def activate_workers(self, workers: Task) -> None:
        value = await workers
        self._Async_Running_Result.append(value)


    @dispatch(Iterable)
    async def activate_workers(self, workers: List[Task]) -> None:
        for worker in workers:
            await self.activate_workers(worker)



if __name__ == '__main__':

    # asyncio_gather()
    # asyncio_run()
    # __async_task_3_newer()

    __async_opt = AsyncOpt()
    __async_opt.run(function=fun_1, args={"param": "new_test_1", "index": "new_1"})
