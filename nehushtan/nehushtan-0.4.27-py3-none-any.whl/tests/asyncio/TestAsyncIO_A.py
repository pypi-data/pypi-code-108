import asyncio

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger

logger = NehushtanFileLogger()


async def async_func_1(task_id: int):
    logger.info("async_func_1 start", task_id)
    await asyncio.sleep(1)
    logger.info("async_func_1 end", task_id)


async def async_func_0():
    task_dict = {}
    for i in range(10):
        # use create_task
        x = asyncio.create_task(async_func_1(i))
        task_dict[i] = x

    logger.info("TASKS CREATED")
    for i in range(10):
        await task_dict[i]

    logger.info("TASKS AWAITED")


if __name__ == '__main__':
    logger.info("main start")
    # they would run in order
    # for i in range(10):
    #     asyncio.run(async_func_1(i))

    asyncio.run(async_func_0())

    logger.info("main end")
