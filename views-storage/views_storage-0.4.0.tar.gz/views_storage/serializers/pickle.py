import pickle
from typing import Any

from . import serializer


class Pickle(serializer.Serializer[Any]):
    def serialize(self, obj: Any) -> bytes:
        return pickle.dumps(obj)

    def deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)
