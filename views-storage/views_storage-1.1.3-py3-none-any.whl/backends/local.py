
import os
from . import storage_backend

class Local(storage_backend.StorageBackend[str, bytes]):

    def store(self, key: str, value: bytes) -> None:
        with open(self._path(key), "wb") as f:
            f.write(value)

    def retrieve(self, key: str):
        with open(self._path(key), "rb") as f:
            return f.read()

    def keys(self):
        return os.listdir(self._root)

    def exists(self, key: str):
        return os.path.exists(self._path(key))

    def __init__(self, root: str):
        self._root = root

    def _path(self, key: str):
        return os.path.join(self._root, key)
