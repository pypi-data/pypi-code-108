from functools import lru_cache
from typing import Dict, Type, Any, Optional

from .serializer import Serializer, TSerializable

# TODO Describe why:
try:
    import serpyco
except ImportError:
    serpyco = None


@lru_cache
def _get_serializer(schema: Type[TSerializable]) -> serpyco.Serializer:
    """
    TODO
    """
    return serpyco.Serializer(schema, strict=True)


# -- Serializers -------------------------------------------------------------


class SerpycoSimpleSerializer(Serializer[Dict[str, Any]]):
    """
    Serialize and deserialize to and from simple Python types (dictionary).
    """
    def serialize(
            self, obj: TSerializable,
            schema: Optional[Type[TSerializable]] = None,
    ) -> Dict[str, Any]:
        """
        Serializes object to Python.
        """
        if schema is None:
            schema = obj.__class__
        return _get_serializer(schema).dump(obj)

    def deserialize(
            self,
            data: Dict[str, Any],
            schema: Type[TSerializable],
            validate: bool = True,
    ) -> TSerializable:
        """
        Deserialize JSON data to instance of type "cls".
        """
        return _get_serializer(schema) \
            .load(data, validate=validate)


class SerpycoJsonSerializer(Serializer[bytes]):
    """
    Serialize and deserialize to and from JSON (encoded bytes).
    """
    def serialize(
            self,
            obj: TSerializable,
            schema: Optional[Type[TSerializable]] = None,
    ) -> bytes:
        """
        Serializes object to JSON.
        """
        if schema is None:
            schema = obj.__class__
        return _get_serializer(schema).dump_json(obj).encode()

    def deserialize(
            self,
            data: bytes,
            schema: Type[TSerializable],
            validate: bool = True,
    ) -> TSerializable:
        """
        Deserialize JSON data to instance of type "cls".
        """
        return _get_serializer(schema) \
            .load_json(data.decode('utf8'), validate=validate)
