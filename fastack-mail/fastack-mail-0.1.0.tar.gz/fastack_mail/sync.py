from typing import Awaitable

import anyio


def run_sync(func: Awaitable, *args, **kwds):
    async def executor():
        return await func(*args, **kwds)

    return anyio.from_thread.run(executor)
