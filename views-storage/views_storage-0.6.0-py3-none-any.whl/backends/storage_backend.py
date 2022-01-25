from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")

class StorageBackend(ABC, Generic[T, U]):
    @abstractmethod
    def store(self, key: T, value: U) -> None:
        raise NotImplementedError()

    @abstractmethod
    def retrieve(self, key: T) -> U:
        raise NotImplementedError()

    @abstractmethod
    def exists(self, key: T) -> bool:
        """
        exists
        ===========

        parameters:
            path (str): Uhe path to a file on the server

        returns:
            bool: Whether file exists or not

        For a given path check if file exists
        """

        raise NotImplementedError()

    @abstractmethod
    def keys(self):
        raise NotImplementedError()
