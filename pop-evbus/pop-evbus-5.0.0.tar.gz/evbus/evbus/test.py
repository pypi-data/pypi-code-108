import asyncio
import datetime
import random
from typing import AsyncGenerator

__func_alias__ = {"print_": "print"}


def __virtual__(hub):
    return (
        False,
        "This sub needs to be explicitly added by ignoring virtuals when it is loaded",
    )


async def listen(hub) -> AsyncGenerator:
    i = 0
    hub.log.debug("started random data injector")
    while hub.evbus.RUN_FOREVER:
        randint = random.randint(0, 10000000)
        yield {
            "number": i,
            "timestamp": datetime.datetime.now().timestamp(),
            "data": f"{randint}".zfill(7),
        }
        i += 1
        await asyncio.sleep(1)


async def start(hub):
    async for event in hub.evbus.test.listen():
        await hub.evbus.broker.put(routing_key="random", body=event)


async def print_(hub, renderer: str = "json"):
    """
    Just print out the internal queue forever
    """
    hub.log.debug("Started evbus print loop")
    while hub.evbus.RUN_FOREVER:
        await asyncio.sleep(0)

        queue: asyncio.Queue
        for routing_key, queue in hub.ingress.internal.QUEUE.items():
            if queue.empty():
                continue
            event = await queue.get()

            print(hub.output[renderer].display((routing_key, event)))
            print("-" * 80)
