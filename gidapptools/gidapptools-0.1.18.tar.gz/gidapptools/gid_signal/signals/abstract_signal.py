"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Hashable
from pathlib import Path
from weakref import WeakSet, WeakMethod, ref

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.helper import get_qualname_or_name

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AdaptableWeakSet(WeakSet):

    def add(self, item) -> None:
        if self._pending_removals:
            self._commit_removals()

        elif inspect.ismethod(item):
            ref_item = WeakMethod(item, self._remove)
        else:
            ref_item = ref(item, self._remove)
        self.data.add(ref_item)

    def __bool__(self) -> bool:
        return self.data is not None and len(self.data) > 0


class AbstractSignal(ABC):

    def __init__(self, key: Hashable, allow_sync_targets: bool = True, allow_async_target: bool = True) -> None:
        self.key = key
        self.allow_sync_targets = allow_sync_targets
        self.allow_async_targets = allow_async_target
        if self.allow_async_targets is False and self.allow_async_targets is False:
            raise AttributeError('A signal cannot have both SYNC and ASYNC targets disabled.')
        self.targets = AdaptableWeakSet()
        self.targets_info: dict[str, dict[str:Any]] = {}

    def _add_target_info(self, target: Callable) -> None:
        info = {'is_coroutine': asyncio.iscoroutine(target)}
        name = get_qualname_or_name(target)
        self.targets_info[name] = info

    def _verify(self, target: Callable) -> None:
        if inspect.isbuiltin(target):
            raise TypeError('cannot weakreference built_ins.')
        target_is_coroutine = asyncio.iscoroutine(target)
        if target_is_coroutine is True and self.allow_async_targets is False:
            raise TypeError('Signal is set to only allow SYNC targets.')
        if target_is_coroutine is False and self.allow_sync_targets is False:
            raise TypeError('Signal is set to only allow ASYNC targets.')

    def connect(self, target: Callable) -> None:
        self._verify(target)
        self._add_target_info(target)
        self.targets.add(target)

    def disconnect(self, target: Callable) -> None:
        name = get_qualname_or_name(target)
        self.targets.discard(target)
        self.targets_info.pop(name)

    @abstractmethod
    def emit(self, *args, **kwargs):
        ...

    @abstractmethod
    async def aemit(self, *args, **kwargs):
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key={self.key!r})"

    def __str__(self):
        return f"{self.__class__.__name__}-{self.key}(targets={self.targets!r})"


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
