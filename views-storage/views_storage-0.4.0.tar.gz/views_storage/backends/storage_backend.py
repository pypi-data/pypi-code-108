from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def store(self, key: str, value: bytes) -> None:
        raise NotImplementedError()

    @abstractmethod
    def retrieve(self, key: str) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        exists
        ===========

        parameters:
            path (str): The path to a file on the server

        returns:
            bool: Whether file exists or not

        For a given path check if file exists
        """

        raise NotImplementedError()

    @abstractmethod
    def keys(self):
        raise NotImplementedError()
