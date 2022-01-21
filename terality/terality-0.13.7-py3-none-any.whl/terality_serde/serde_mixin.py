from __future__ import annotations
import asyncio
import base64
from enum import Enum
import re
import zlib
import inspect
import json
import sys
from typing import Any, Dict, Optional, Set, Type, Union, List

from terality_serde.protobuf_wrapper import ProtobufWrapper
from terality_serde import TeralityDeserializationError

from . import TeralitySerializationError, all_external_types, external_base_classes, TypeSerde


_HAS_CACHED_PROPERTIES = sys.version_info[1] >= 8
if _HAS_CACHED_PROPERTIES:
    from functools import cached_property


# Subclasses of SerdeMixin can't be serialized in multiple threads in parallel
# (this mixin is not thread safe)
class SerdeMixin:
    subclasses: List[Type[SerdeMixin]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @classmethod
    def _cached_properties_names(cls) -> Set[str]:
        # inspect.getmembers is expensive and dominate execution times if not cached
        if (
            not hasattr(cls, "_cached_properties_names_cache")
            or cls._cached_properties_names_cache is None  # type: ignore[attr-defined]
        ):
            cls._cached_properties_names_cache = {  # type: ignore[attr-defined]
                k for k, v in inspect.getmembers(cls) if isinstance(v, cached_property)
            }
        return cls._cached_properties_names_cache  # type: ignore[attr-defined]

    @property
    def dict(self) -> Dict:
        if _HAS_CACHED_PROPERTIES:
            dict_ = {
                k: v for k, v in self.__dict__.items() if k not in self._cached_properties_names()
            }
        else:
            dict_ = dict(self.__dict__)
        return dict_

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)


class SerializableEnum(SerdeMixin, Enum):
    """An Enum that is also serializable.

    Usage:
    >>> class MySerializableEnum(SerializableEnum):
            VARIANT_1 = "VARIANT_1"
            VARIANT_2 = "VARIANT_2"
    """

    @property
    def dict(self) -> Dict:
        dict_ = {"name": self.name}
        return dict_

    @classmethod
    def from_dict(cls, name: str) -> SerializableEnum:  # type: ignore
        return cls[name]


class _SerdeConfig:
    """Store the known serialized and deserializer for various types, and apply them to objects.

    This class is immutable and a single instance can be reused.  For performance reasons, do not instantiate
    this class in tight loops.

    Note: the naming of this class implies that it's only configuration, but it actually contains business
    logic. Additionally, the naming of methods and attributes is all over the place ("serializers" are actually "encoders").
    Cleaning that up is TODO.
    """

    def __init__(self, all_external_types_):
        self._internal_type_attribute = "!terality:internal_type"
        self._external_type_attribute = "!terality:external_type"
        self._external_types = all_external_types_
        self._external_base_types = external_base_classes
        self._external_types_to_serializer = {ex.class_: ex for ex in all_external_types_}
        self._external_type_names_to_deserializer = {
            ex.class_name: ex for ex in self._external_types + self._external_base_types
        }
        self._internal_types_cached = None

    def _step_1_protobuf(self, obj: ProtobufWrapper):
        dict_ = {"protobuf": obj.serialize(), self._internal_type_attribute: obj.__class__.__name__}
        return dict_

    def _step_1_serde(self, obj: Any):
        dict_ = obj.dict
        dict_[self._internal_type_attribute] = obj.class_name
        return dict_

    def _step_2_serde(self, obj: Any):
        if isinstance(obj, dict) and all((isinstance(key, str) for key in obj.keys())):
            return obj

        external_type = self._external_types_to_serializer[type(obj)]
        dict_ = external_type.to_json(obj)
        dict_[self._external_type_attribute] = external_type.class_name
        return dict_

    def _step_3_serde(self, base_class, obj):
        dict_ = base_class.to_json(obj)
        dict_[self._external_type_attribute] = base_class.class_name
        return dict_

    def encode(self, obj: Any) -> Union[dict, Any]:
        """
        Encode an Python object to a JSON-serializable value.

        Objects of known types (types with a registered serializer) will be encoded to a dict.
        Objects of types that are already JSON-serializable and types without any registered serializer will be returned
        as-it.

        To fully encode an object to a JSON-serializable value, this function needs to be called recursively
        on any dicts or lists returned by this function (see `serialize`).
        """
        if isinstance(obj, ProtobufWrapper):
            proto = self._step_1_protobuf(obj)
            return proto

        if isinstance(obj, SerdeMixin):
            return self._step_1_serde(obj)

        type_ = type(obj)

        if type_ in self._external_types_to_serializer:
            return self._step_2_serde(obj)

        for base_class in self._external_base_types:
            if issubclass(type_, base_class.class_):
                return self._step_3_serde(base_class, obj)

        return obj

    def encode_recursively(self, obj):
        """Try to return a JSON-serializable representation of this object.

        Calls `encode` recursively. If no unknown types are encountered, the result is a JSON-serializable list, dict
        or scalar.

        Complex types will be encoded as dicts (see `encode`), then `encode` will be called recursively on the keys and
        values of the resulting dictionary (this allows encoding collections of arbitrary objects).

        The result of this function may not be JSON-serializable if this recursive process encounters types
        without any registered serializer.
        """
        encoded = self.encode(obj)

        if isinstance(encoded, list):
            return [self.encode_recursively(elt) for elt in encoded]
        if isinstance(encoded, dict):
            return {
                self.encode_recursively(k): self.encode_recursively(v) for k, v in encoded.items()
            }
        return encoded

    @property
    def _internal_types(self) -> Dict[str, Type[SerdeMixin]]:
        # Put in a property so that it gets computed at runtime at the last minute before it is needed
        # We do this because the problem of the subclasses registration is that it only happens if the subclass gets
        # imported in an __init__ somewhere, so we compute this function at the latest moment to give a chance for
        # the subclasses to have be imported
        if self._internal_types_cached is None:
            self._internal_types_cached = {
                internal.__name__: internal for internal in SerdeMixin.subclasses
            }
        return self._internal_types_cached

    @property
    def _protobuf_wrapper_types(self) -> Dict[str, Type[ProtobufWrapper]]:
        return {protobuf.__name__: protobuf for protobuf in ProtobufWrapper.subclasses}

    def decode(self, encoded: Dict[str, Any]):
        """Reverse of `encode`. Call this as `json.loads(object_hook=SerdeConfig().decode)`.

        Mutate `encoded`.
        """

        if self._internal_type_attribute in encoded:
            internal_type_name = encoded.pop(self._internal_type_attribute)

            # Detecting protobuf objects mixed with SerdeMixin
            if internal_type_name in self._protobuf_wrapper_types:
                protobuf_type = self._protobuf_wrapper_types[internal_type_name]
                return protobuf_type.parse(encoded["protobuf"])

            internal_type = self._internal_types[internal_type_name]
            try:
                return internal_type.from_dict(**encoded)
            except Exception as e:
                raise TeralityDeserializationError(
                    f"Can not instantiate an object of type {internal_type_name} with parameters {encoded}"
                ) from e

        if self._external_type_attribute in encoded:
            external_type_name = encoded.pop(self._external_type_attribute)
            deserializer = self._external_type_names_to_deserializer[external_type_name]
            try:
                return deserializer.from_json(**encoded)
            except Exception as e:
                raise TeralityDeserializationError(
                    f"Can not instantiate an object of type {external_type_name} with parameters {encoded}"
                ) from e

        return encoded


_SERDE_CONFIG = _SerdeConfig(all_external_types + [TypeSerde()])


# pylint: disable=invalid-name
def dumps(o: Any, compressed: bool = False, config: _SerdeConfig = _SERDE_CONFIG) -> str:
    o = config.encode_recursively(o)
    try:
        result = json.dumps(o)
    except TypeError as e:
        unserializable_type = _parse_json_type_error(e)
        if unserializable_type is not None:
            raise TeralitySerializationError(
                f"Can not serialize an object (or a collection or object containing such a type) of type'{unserializable_type}'\n{o}",
                unserializable_type=unserializable_type,
            ) from e
        raise TeralitySerializationError(
            f"Couldn't serialize the provided Python object: {str(e)}"
        ) from e
    if compressed:
        result = base64.encodebytes(zlib.compress(result.encode("utf-8"))).decode("utf-8")
    return result


# pylint: disable=invalid-name
def loads(s: str, compressed: bool = False, config: _SerdeConfig = _SERDE_CONFIG) -> Any:
    if compressed:
        s = zlib.decompress(base64.decodebytes(s.encode("utf-8"))).decode("utf-8")
    return json.loads(s, object_hook=config.decode)


def _parse_json_type_error(e: TypeError) -> Optional[str]:
    """Return the unserializable type that caused the JSON module to throw an error.

    The exception message should look like: "Object of type xxx is not JSON serializable".

    Returns None is the exception message could not be parsed.
    """
    if len(e.args) != 1 or not isinstance(e.args[0], str):
        return None
    message = e.args[0]
    match = re.compile(r"^Object of type (.*) is not JSON serializable$").match(message)
    if match is None:
        return None
    return match.group(1)


# pylint: disable=invalid-name
async def dumps_async(o: Any, compressed: bool = False) -> str:
    return await asyncio.get_event_loop().run_in_executor(None, dumps, o, compressed)


# pylint: disable=invalid-name
async def loads_async(
    s: str,
    compressed: bool = False,
) -> Any:
    return await asyncio.get_event_loop().run_in_executor(None, loads, s, compressed)
