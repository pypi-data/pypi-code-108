import asyncio
import json
from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncIterator, Final, Hashable
from weakref import WeakValueDictionary

__all__ = ('json_dumps', 'get_python_version', 'get_software', 'KeyLock')


json_dumps: Final = partial(json.dumps, ensure_ascii=False)


def get_python_version() -> str:
    from sys import version_info as version
    return f'{version.major}.{version.minor}.{version.micro}'


def get_software() -> str:
    from . import __version__
    return f'Python/{get_python_version()} aiotgbot/{__version__}'


class KeyLock:

    def __init__(self) -> None:
        self._locks: ('Final[WeakValueDictionary[Hashable,'
                      'asyncio.Lock]]') = WeakValueDictionary()

    @asynccontextmanager
    async def resource(self, key: Hashable) -> AsyncIterator[None]:
        if key not in self._locks:
            lock = asyncio.Lock()
            self._locks[key] = lock
        else:
            lock = self._locks[key]
        async with lock:
            yield
