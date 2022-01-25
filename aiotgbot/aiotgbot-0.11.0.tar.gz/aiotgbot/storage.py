from abc import abstractmethod
from typing import (Any, AsyncIterator, Dict, List, Protocol, Tuple, Union,
                    runtime_checkable)

__all__ = ('Json', 'StorageProtocol')

Json = Union[str, int, float, bool, Dict[str, Any], List[Any], None]


@runtime_checkable
class StorageProtocol(Protocol):

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def set(self, key: str, value: Json = None) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> Json: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    def iterate(self, prefix: str = '') -> AsyncIterator[Tuple[str, Json]]: ...

    @abstractmethod
    async def clear(self) -> None: ...
