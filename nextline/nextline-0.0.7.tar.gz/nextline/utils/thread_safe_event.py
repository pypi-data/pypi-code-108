import asyncio


##__________________________________________________________________||
class ThreadSafeAsyncioEvent(asyncio.Event):
    """A thread-safe asyncio event

    Code copied from
    https://stackoverflow.com/a/33006667/7309855

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._loop is None:  # Python 3.10
            self._loop = asyncio.get_event_loop()

    def set(self):
        self._loop.call_soon_threadsafe(super().set)

    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)


##__________________________________________________________________||
