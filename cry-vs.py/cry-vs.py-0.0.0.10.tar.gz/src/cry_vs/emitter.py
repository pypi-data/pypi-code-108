import asyncio
import datetime
import logging
import queue

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    for handler in logging.getLogger().handlers:
        logger.addHandler(handler)


# this class is chemically bound to the client it was created with
# it is responsible for sending messages to the client
class Emitter:
    q = queue.Queue()
    loop = asyncio.get_event_loop()

    def __init__(
            self,
            funcs,
            client=None,
            events=None,
            ):
        if events is None:
            events = [
                "any_event",
                "on_ready",
                "before_expire",
            ]
        self.funcs = funcs
        self.client = client
        self.events = events

    def queue(self):
        while True:
            if self.client.auth.token.time < datetime.datetime.now() + datetime.timedelta(seconds=2) and self.client.keep_alive:
                logging.info("token about to expire. refreshing...")
                for func in self.funcs:
                    if func.__name__ == "before_expire":
                        asyncio.run(func(self.client))


            if self.q.empty():
                continue
            logger.debug(f"Emitter has {self.q.qsize()} events in queue")
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

    def enqueue(self, name, args: list = None):
        if args is None:
            args = []
        self.q.put(item=[name, args])
