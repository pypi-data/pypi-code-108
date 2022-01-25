from typing import Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar("T")
U = TypeVar("U")

class Serializer(ABC, Generic[T,U]):
    @abstractmethod
    def serialize(self, obj: T) -> U:
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, data: U) -> T:
        raise NotImplementedError
