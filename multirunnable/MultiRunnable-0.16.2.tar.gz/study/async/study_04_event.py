import asyncio
import random


async def waiter(event: asyncio.Event):
    while True:
        await asyncio.sleep(2)
        print("[Waiter] This is waiter who will wait for sender give a message....")
        await event.wait()
        print("[Waiter] Waiter got a message from sender!")
        is_set_flag = event.is_set()
        print("[Waiter] event is_set: ", is_set_flag)
        print("[Waiter] clean event")
        event.clear()
        is_set_flag = event.is_set()
        print("[Waiter] event is_set: ", is_set_flag)


async def sender(event: asyncio.Event):
    while True:
        print("[Sender] This is sender who will keep sending message.")
        print("[Sender] Asleep when sending message ... ")
        _sleep_time = random.randrange(1, 10)
        print("[Sender] Sleep time: ", _sleep_time)
        await asyncio.sleep(_sleep_time)
        event.set()
        print("[Sender] Send a message!")



async def running():
    event = asyncio.Event()
    async_waiter = asyncio.create_task(waiter(event))
    async_sender = asyncio.create_task(sender(event))

    await async_waiter
    await async_sender



if __name__ == '__main__':

    asyncio.run(running())
