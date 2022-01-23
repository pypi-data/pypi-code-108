from typing import List
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
    asyncio.run(run_fun())



async def __async_task_1():
    _task_1 = asyncio.create_task(fun_1(param="test_1", index="1"))
    value = await _task_1
    print("Task_1: ", value)



async def __async_task_2():
    _task_2 = asyncio.create_task(fun_2(param="test_2", index="2"))
    value = await _task_2
    print("Task_2: ", value)



def asyncio_run():
    asyncio.run(__async_task_1())
    asyncio.run(__async_task_2())    # Will be blocking run



class AsyncOpt:

    """
    2 strategy: asyncio.run or asyncio.event_loop
    """

    __Running_Time = 0

    @classmethod
    def run(cls, running_time: int) -> None:
        cls.__Running_Time = running_time
        asyncio.run(cls._wrap_to_task())


    @classmethod
    async def _wrap_to_task(cls, function=None, *args, **kwargs) -> List:
        return [asyncio.create_task(function(*args, **kwargs)) for _ in range(cls.__Running_Time)]



if __name__ == '__main__':

    asyncio_gather()
    # asyncio_run()
