import asyncio
import queue
import sys


class Emitter:
    q = queue.Queue()
    loop = asyncio.get_event_loop()

    def __init__(self,
                 funcs,
                 expire,
                 events=[
                     "any_event",
                     "on_ready",
                     "on_exit"
                 ],
                 ):
        self.funcs = funcs
        self.events = events

    def queue(self):
        while True:
            if self.q.empty(): continue
            curr = self.q.get()
            for func in self.funcs:
                if func.__name__ in self.events and func.__name__ == curr[0].lower():
                    try:
                        asyncio.run(func(curr[1]))
                    except TypeError:
                        asyncio.run(func())

                if func.__name__ == "any_event":
                    try:
                        asyncio.run(func(curr[1]))
                    except TypeError:
                        asyncio.run(func())

    def enqueue(self, name, args=[]):
        self.q.put(item=[name, args])