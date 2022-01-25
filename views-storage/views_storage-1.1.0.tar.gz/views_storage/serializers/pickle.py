import pickle
from typing import Any
import lz4.frame
from . import serializer


class Pickle(serializer.Serializer[Any, bytes]):
    def __init__(self, compression = True):
        """
        Pickle
        ======

        parameters:
            compression (bool): Whether to compress the serialized data using Gzip
        """
        self._compression = compression

    def serialize(self, obj: Any) -> bytes:
        data = pickle.dumps(obj)
        if self._compression:
            data = lz4.frame.compress(data)
        return data

    def deserialize(self, data: bytes) -> Any:
        if self._compression:
            data = lz4.frame.decompress(data)
        return pickle.loads(data)
