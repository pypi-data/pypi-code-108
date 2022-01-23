import asyncio
import random
import time



class AsyncAClass:

    async def fun_1(self):
        print("This is function AsyncA.fun_1")
        sleep_time = random.randrange(1, 10)
        print(f"AsyncA.fun_1 Will sleep for {sleep_time} seconds ...")
        await asyncio.sleep(sleep_time)
        print(f"AsyncA.fun_1 end, time: {time.time()}")



class AsyncBClass:

    async def fun_2(self):
        print("This is function AsyncB.fun_2")
        __C = AsyncCClass()
        print("AsyncB.fun_2 call AsyncC.fun_3")
        result = await __C.fun_3()
        print(f"Result: {result}")



class AsyncCClass:

    async def fun_3(self):
        print("This is function AsyncC.fun_3")
        sleep_time = random.randrange(1, 10)
        print(f"AsyncC.fun_3 Will sleep for {sleep_time} seconds ...")
        await asyncio.sleep(sleep_time)
        print(f"AsyncC.fun_3 end, time: {time.time()}")
        return "Test Result"



class AsyncMainWithRun:

    # __A = AsyncAClass()
    __B = AsyncBClass()
    __C = AsyncCClass()

    def __init__(self, test_cls: AsyncAClass):
        self.test_cls = test_cls

    def main_run(self):
        asyncio.run(self.dispatcher())


    async def dispatcher(self):
        await asyncio.gather(self.test_cls.fun_1(), self.__B.fun_2(), self.__C.fun_3())



class AsyncMainWithEventLoop:

    __B = AsyncBClass()
    __C = AsyncCClass()
    __Event_Loop = None

    def __init__(self, test_cls: AsyncAClass):
        self.test_cls = test_cls


    def main_run(self):
        self.__Event_Loop = asyncio.get_event_loop()
        self.__Event_Loop.run_until_complete(future=self.dispatcher())


    async def dispatcher(self):
        tasks = [self.__Event_Loop.create_task(self.test_cls.fun_1()), self.__Event_Loop.create_task(self.__B.fun_2())]
        await asyncio.wait(tasks)


if __name__ == '__main__':

    __A = AsyncAClass()
    # __async_main = AsyncMainWithRun(test_cls=__A)
    __async_main = AsyncMainWithEventLoop(test_cls=__A)
    __async_main.main_run()
