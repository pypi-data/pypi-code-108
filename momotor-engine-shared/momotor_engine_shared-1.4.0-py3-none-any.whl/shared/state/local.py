import asyncio
from contextlib import asynccontextmanager
import typing
import weakref

from momotor.shared.exlock import ExLock
from .base import StateABC
from ..doc import annotate_docstring
from ..log import getAsyncLogger

logger = getAsyncLogger(__name__)


@annotate_docstring(logger=logger)
class LocalState(StateABC):
    """ Reference implementation of :py:class:`~momotor.shared.state.StateABC` for local use.

    Uses a :py:class:`~weakref.WeakValueDictionary` of :py:class:`momotor.shared.exlock.ExLock` objects.

    Produces debug logging information on the ``{logger.name}`` logger
    """
    def __init__(self):
        self.__dict_lock = asyncio.Lock()
        self.__locks: typing.MutableMapping[str, ExLock] = weakref.WeakValueDictionary()

    async def _get_rwlock(self, key: str, create: bool):
        async with self.__dict_lock:
            lock = self.__locks.get(key)
            if lock is None and create:
                lock = self.__locks[key] = ExLock()

        return lock

    @asynccontextmanager
    async def get_lock(self, key: str, *, exclusive: bool = True) -> typing.AsyncContextManager[None]:
        # Need to keep a reference to the full rwlock, not just the reader or writer lock, otherwise
        # the WeakValueDictionary will delete the rwlock even though we have the reader or writer locked
        # using async-with causes similar problems, therefor using acquire and release

        exlock = await self._get_rwlock(key, True)
        await logger.debug(f'state lock {key}{" exclusive" if exclusive else ""} acquiring {exlock}')

        await exlock.get(exclusive).acquire()
        await logger.debug(f'state lock {key}{" exclusive" if exclusive else ""} acquired {exlock}')

        try:
            yield
        finally:
            exlock.get(exclusive).release()
            await logger.debug(f'state lock {key}{" exclusive" if exclusive else ""} released {exlock}')

    async def test_lock(self, key: str, *, exclusive: bool = True) -> bool:
        exlock = await self._get_rwlock(key, False)
        return exlock.get(exclusive).locked if exlock else False
