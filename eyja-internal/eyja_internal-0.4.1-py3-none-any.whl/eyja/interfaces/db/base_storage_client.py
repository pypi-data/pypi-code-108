from typing import Any


class BaseStorageClient:
    _config_cls = dict
    _config: Any
    _buckets: list

    def __init__(self, config: dict):
        self._config = self._config_cls(**config)
        self._buckets = []

    async def init(self):
        pass

    async def save(self, obj, object_space, object_type):
        pass

    async def delete(self, obj, object_space, object_type):
        pass

    async def delete_all(self, obj, object_space, object_type, filter):
        pass

    async def get(self, obj_cls, object_space, object_type, object_id):
        pass

    async def find(self, obj_cls, object_space, object_type, filter):
        pass

    async def count(self, obj_cls, object_space, object_type, filter):
        pass
