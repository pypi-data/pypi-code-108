from abc import ABC
from typing import Generic, TypeVar
from .serializers import serializer
from .backends import storage_backend

T = TypeVar("T")


class KeyValueStore(Generic[T]):
    """
    KeyValueStore
    =============

    Abstract class for a key-value store combining a storage backend with a
    serializer-deserializer. Generalizes key-value storage across multiple
    backends.

    Subclasses should override __init__, setting the self.backend and
    self.serializer values to subclasses of storage_backend.StorageBackend and
    serializer.Serializer respectively.
    """

    def __init__(self, backend: storage_backend.StorageBackend, serializer: serializer.Serializer):
        self.backend = backend
        self.serializer = serializer

    def exists(self, key: str) -> bool:
        return self.backend.exists(key)

    def write(self, key: str, value: T, overwrite: bool = False):
        if self.exists(key) and not overwrite:
            raise FileExistsError("File exists, overwrite is False")

        self.backend.store(key, self.serializer.serialize(value))

    def read(self, key: str) -> T:
        try:
            raw = self.backend.retrieve(key)
            assert raw is not None
        except (KeyError, AssertionError):
            raise KeyError(f"{key} does not exist")
        return self.serializer.deserialize(raw)

    def list(self):
        return self.backend.keys()
