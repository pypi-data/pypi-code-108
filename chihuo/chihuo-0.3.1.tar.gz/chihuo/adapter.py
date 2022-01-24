from typing import Any
from abc import ABC, abstractmethod

from lodis_py.client import AsyncLodisClient


class Wrapper(ABC):
    @abstractmethod
    async def exists(self, key) -> bool:
        """Check whether the key exists in the queue"""
        raise NotImplementedError

    @abstractmethod
    async def push_left(self, key, value) -> None:
        """Add tasks to the left of the queue"""
        raise NotImplementedError

    @abstractmethod
    async def pushnx_left(self, key, value) -> None:
        """Add tasks to the left of the queue only if item does not exists in the queue"""
        raise NotImplementedError

    @abstractmethod
    async def push(self, key, value) -> None:
        """Add tasks to the right of the queue"""
        raise NotImplementedError

    @abstractmethod
    async def pushnx(self, key, value) -> None:
        """Add tasks to the right of the queue only if item does not exists in the queue"""
        raise NotImplementedError

    @abstractmethod
    async def pop_left(self) -> Any:
        """Take out an task from the left of the queue"""
        raise NotImplementedError

    @abstractmethod
    async def pop(self) -> Any:
        """Take out an task from the right of the queue"""
        raise NotImplementedError

    @abstractmethod
    async def size(self) -> int:
        """The size of the queue"""
        raise NotImplementedError

    @abstractmethod
    async def finish(self, key) -> None:
        """Set the task which has the key to finished"""
        raise NotImplementedError

    @abstractmethod
    async def finished(self, key) -> bool:
        """Check whether a task is finished"""
        raise NotImplementedError

    @abstractmethod
    async def unfinish(self, key) -> None:
        """Set the task which has the key to unfinished"""
        raise NotImplementedError

    @abstractmethod
    async def clear_unfinished_tasks(self) -> None:
        """Clear all unfinished tasks from the queue"""
        raise NotImplementedError

    @abstractmethod
    async def clear_finished_tasks(self) -> None:
        """Clear all finished tasks"""
        raise NotImplementedError

    async def clear_all(self) -> None:
        """Clear all unfinished and finished tasks"""

        await self.clear_unfinished_tasks()
        await self.clear_finished_tasks()


class LodisWrapper(Wrapper):
    def __init__(self, namespace, ip, port, loop=None):
        self._lodis = AsyncLodisClient(namespace, ip, port, loop=loop)

    # ArrayMap
    async def exists(self, key) -> bool:
        resp = await self._lodis.aexists(key)
        return resp.value()  # type: ignore

    async def push_left(self, *pairs) -> None:
        await self._lodis.alpush(*pairs)

    async def pushnx_left(self, *pairs) -> None:
        await self._lodis.alpushnx(*pairs)

    async def push(self, *pairs) -> None:
        await self._lodis.arpush(*pairs)

    async def pushnx(self, *pairs) -> None:
        await self._lodis.arpushnx(*pairs)

    async def pop_left(self) -> Any:
        resp = await self._lodis.alpop()
        return resp.value()  # type: ignore

    async def pop(self) -> Any:
        resp = await self._lodis.arpop()
        return resp.value()  # type: ignore

    async def size(self) -> int:
        resp = await self._lodis.alen()
        return resp.value()  # type: ignore

    # Map
    async def finish(self, *keys) -> None:
        pairs = [(key, b"") for key in keys]
        await self._lodis.hmset(*pairs)

    async def finished(self, key) -> bool:
        resp = await self._lodis.hexists(key)
        return resp.value()  # type: ignore

    async def unfinish(self, key) -> None:
        await self._lodis.hdel(key)

    async def clear_unfinished_tasks(self) -> None:
        await self._lodis.arm()

    async def clear_finished_tasks(self) -> None:
        await self._lodis.hrm()
