import json
from typing import Union, List, Dict
from . import serializer

JsonSerializable = Union[
        Dict["JsonSerializable","JsonSerializable"],
        List["JsonSerializable"],
        str, int, float, bool, None]

class Json(serializer.Serializer[JsonSerializable, bytes]):

    def serialize(self, obj: JsonSerializable):
        return json.dumps(obj).encode()

    def deserialize(self, data: bytes) -> JsonSerializable:
        return json.loads(data)
