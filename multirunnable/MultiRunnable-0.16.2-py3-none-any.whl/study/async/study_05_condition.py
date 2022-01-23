import asyncio
import random


async def waiter(condition: asyncio.Condition):
    while True:
        await asyncio.sleep(2)
        print("[Waiter] This is waiter who will wait for sender give a message....")
        async with condition:
            await condition.wait()
            print("[Waiter] Waiter got a message from sender!")


async def sender(condition: asyncio.Condition):
    while True:
        print("[Sender] This is sender who will keep sending message.")
        print("[Sender] Asleep when sending message ... ")
        _sleep_time = random.randrange(1, 10)
        print("[Sender] Sleep time: ", _sleep_time)
        await asyncio.sleep(_sleep_time)
        async with condition:
            condition.notify_all()
        print("[Sender] Send a message!")



async def running():
    condition = asyncio.Condition()
    async_waiter = asyncio.create_task(waiter(condition))
    async_sender = asyncio.create_task(sender(condition))

    await asyncio.wait(async_waiter)
    await asyncio.wait(async_sender)

    # await async_waiter
    # await async_sender



if __name__ == '__main__':

    asyncio.run(running())
