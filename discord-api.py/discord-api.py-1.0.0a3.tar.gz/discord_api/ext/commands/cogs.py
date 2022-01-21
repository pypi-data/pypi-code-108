from typing import Union
from inspect import getmembers
import asyncio

class Cog:
    @classmethod
    def listener(cls, name = None):
        def deco(coro):
            if not asyncio.iscoroutinefunction(coro):
                raise TypeError("Use a coroutine function")
            if name is None:
                coro._cog_listener = coro.__name__
            else:
                coro._cog_listener = name
            return coro
        return deco

    def setup(self, bot):
        for n, coro in getmembers(self):
            if hasattr(coro, "_cog_listener"):
                bot.add_listener(coro, coro._cog_listener)
        return self
