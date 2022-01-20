from typing import Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar("T")


class Serializer(ABC, Generic[T]):
    @abstractmethod
    def serialize(self, obj: T) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, data: bytes) -> T:
        raise NotImplementedError
