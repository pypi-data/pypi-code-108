import asyncio
import inspect
import logging
import typing
import weakref
from abc import abstractmethod

from momotor.shared.exlock import ExLock
from momotor.shared.log import getAsyncLogger, async_log_exception

KT = typing.TypeVar('KT', bound=typing.Hashable)  # Key type
LT = typing.TypeVar('LT', asyncio.Lock, ExLock)  # Lock type


logger = getAsyncLogger(__name__)


class SetLock:
    def __init__(self, lock_ref, lock, exclusive, log_label):
        self.__lock_ref = lock_ref  # Reference to the base lock. Needed to keep the weakref in the LockSet alive for ExLocks
        self.__lock = lock
        self.__exclusive = exclusive
        self.__log_label = log_label
        self.__locked = False

    @property
    def exclusive(self) -> bool:
        return self.__exclusive

    @property
    def locked(self) -> bool:
        return self.__locked

    if logger.isEnabledFor(logging.DEBUG):
        async def acquire(self):
            await logger.debug(f'{self.__log_label} acquiring')
            await self.__lock.acquire()
            self.__locked = True
            await logger.debug(f'{self.__log_label} acquired')

        def release(self):
            logger.sync.debug(f'{self.__log_label} releasing')
            self.__lock.release()
            self.__locked = False
            logger.sync.debug(f'{self.__log_label} released')
    else:
        async def acquire(self):
            await self.__lock.acquire()
            self.__locked = True

        def release(self):
            self.__lock.release()
            self.__locked = False

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(self, *args) -> None:
        self.release()


class LockSetBase(typing.Generic[KT, LT]):
    __locks: typing.MutableMapping[KT, LT]

    def __init__(self, set_name: str):
        self.set_name = set_name
        self.__locks = weakref.WeakValueDictionary()

    @staticmethod
    def _get_caller_name(level=2):
        try:
            frame_info = inspect.stack()[level]
        except KeyError:
            return '(unknown)'

        try:
            package = frame_info.frame.f_globals["__package__"]
        except (AttributeError, KeyError):
            return frame_info.function
        else:
            return f'{package}.{frame_info.function}'

    @abstractmethod
    def _new_lock(self) -> LT:
        ...

    def _get_or_create(self, key: KT) -> typing.Tuple[LT, bool]:
        lock = self.__locks.get(key)
        if lock:
            created = False
        else:
            self.__locks[key] = lock = self._new_lock()
            created = True

        return lock, created


class LockSet(LockSetBase[KT, asyncio.Lock], typing.Generic[KT]):
    def _new_lock(self) -> asyncio.Lock:
        return asyncio.Lock()

    async def get(self, key: KT, *, caller_name: str = None, log_key: str = None) -> SetLock:
        async with async_log_exception(logger, 'LockSet.get'):
            if not caller_name and logger.isEnabledFor(logging.DEBUG):
                caller_name = self._get_caller_name()

            lock, created = self._get_or_create(key)

            log_label = f'{caller_name}: {self.set_name} lock set key {log_key or key!r}'

            await logger.debug(
                f'{log_label} {"created" if created else "reusing"} lock'
            )

            return SetLock(lock, lock, True, log_label)


ExclusiveType = typing.Union[bool, typing.Callable[[KT, bool], typing.Coroutine[None, None, bool]]]


class ExLockSet(LockSetBase[KT, ExLock], typing.Generic[KT]):
    def _new_lock(self) -> ExLock:
        return ExLock()

    async def get(self, key: KT, exclusive: ExclusiveType, *, caller_name: str = None, log_key: str = None) -> SetLock:
        async with async_log_exception(logger, 'ExLockSet.get'):
            if not caller_name and logger.isEnabledFor(logging.DEBUG):
                caller_name = self._get_caller_name()

            lock, created = self._get_or_create(key)

            if callable(exclusive):
                exclusive = await exclusive(key, created)

            log_label = f'{caller_name}: {self.set_name} lock set key {log_key or key!r}' \
                        f'{" (exclusive)" if exclusive else ""}'

            await logger.debug(
                f'{log_label} {"created" if created else "reusing"} lock'
            )

            return SetLock(lock, lock.get(exclusive), exclusive, log_label)
