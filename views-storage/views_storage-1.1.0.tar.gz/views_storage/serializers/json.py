import json
from typing import Union, List, Dict
from views_storage import types
from . import serializer

class Json(serializer.Serializer[types.JsonSerializable, bytes]):

    def serialize(self, obj: types.JsonSerializable):
        return json.dumps(obj).encode()

    def deserialize(self, data: bytes) -> types.JsonSerializable:
        return json.loads(data)
