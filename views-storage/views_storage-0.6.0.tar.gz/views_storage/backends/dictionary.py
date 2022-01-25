
from . import storage_backend


class DictBackend(storage_backend.StorageBackend[str, bytes]):
    def __init__(self):
        self._dict = {}
        super().__init__()

    def store(self, key: str, value: bytes) -> None:
        self._dict[key] = value

    def retrieve(self, key: str) -> bool:
        return self._dict[key]

    def exists(self, key: str) -> bool:
        return key in self._dict

    def keys(self):
        return list(self._dict.keys())
