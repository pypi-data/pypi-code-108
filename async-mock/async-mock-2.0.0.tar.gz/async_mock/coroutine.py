import asyncio
from unittest.mock import MagicMock

def SimpleCoroutineMock(f=lambda *args, **kwargs: None):
    builder = CoroutineMockBuilder()
    return builder.addDelegate(f).build().mock()


class CoroutineMock(object):

    # Handy for debugging failing tests in the debugger.
    __blocking_dict = {}

    def __init__(self, returnSequence, block:asyncio.Event):
        self.__startingEvent = asyncio.Event()
        self.__endingEvent = asyncio.Event()
        self.__returnSequence = tuple(returnSequence)
        if (len(self.__returnSequence) < 1):
            self.__returnSequence = (lambda *args, **kwargs: None, )
        self.__returnSequenceLen = len(self.__returnSequence)
        self.__block = block
        self.__mock = self.__createMock()
        # It's easier to find a dictionary that is an instance variable than
        # one that is a class static, so just make an instance variable that
        # references the shared dictionary.
        self.__blocking_dict = CoroutineMock.__blocking_dict

    def __createMock(self):
        returnIndex = 0

        async def cr(*args, **kwargs):
            nonlocal returnIndex
            try:
                self.__endingEvent.clear()
                self.__startingEvent.set()
                if (self.__block is not None):
                    self.__blocking_dict[id(self)] = self
                    try:
                        await self.__block.wait()
                    finally:
                        del self.__blocking_dict[id(self)]
                    self.__block.clear()
                returnFunc = self.__returnSequence[returnIndex % self.__returnSequenceLen]
                returnIndex += 1
                return returnFunc(*args, **kwargs)
            finally:
                self.__startingEvent.clear()
                self.__endingEvent.set()

        return MagicMock(wraps=cr)

    def start(self):
        return self.__startingEvent

    def end(self):
        return self.__endingEvent

    def unblock(self):
        self.__block.set()

    def mock(self):
        return self.__mock

    async def waitForSingleCall(self):
        await self.start().wait()
        self.unblock()
        await self.end().wait()


class CoroutineMockBuilder(object):
    def __init__(self):
        self.__block = None
        self.__returnSequence = []

    def blocks(self):
        return self.blocksOn(asyncio.Event())

    def blocksOn(self, event:asyncio.Event):
        self.__block = event
        return self

    def exception(self, e, repeats=1):
        def r(*args, **kwargs):
            raise e
        self.__returnSequence.extend([r] * repeats)
        return self

    def returns(self, v, repeats=1):
        def r(*args, **kwargs):
            return v
        self.__returnSequence.extend([r] * repeats)
        return self

    def addDelegate(self, f, repeats=1):
        self.__returnSequence.extend([f] * repeats)
        return self

    def build(self):
        return CoroutineMock(self.__returnSequence, self.__block)
