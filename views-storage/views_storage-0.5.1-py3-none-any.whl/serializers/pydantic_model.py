from typing import TypeVar, Generic
from . import serializer
from ..backends import postgres_json_backend

T = TypeVar("T")

class PydanticModel(serializer.Serializer, Generic[T]):
    def serialize(self, obj: T)-> postgres_json_backend.JsonSerializable:
        return obj.dict()

    def deserialize(self, data: postgres_json_backend.JsonSerializable) -> T:
        return T(**data)
