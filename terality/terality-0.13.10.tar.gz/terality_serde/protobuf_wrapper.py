from __future__ import annotations
from abc import ABC, abstractmethod
from typing import ByteString, List, Type


class ProtobufWrapper(ABC):
    """A Wrapper around a protobuf object for efficient serialization"""

    _protobuf_class: Type
    subclasses: List[Type[ProtobufWrapper]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @property
    @abstractmethod
    def proto(self):
        """Returns protobuf object wrapping containing current object's data"""

    @classmethod
    @abstractmethod
    def from_proto(cls, proto) -> ProtobufWrapper:
        """Returns an instance of the ProtobufWrapper subclass initialized using the data provided inside the proto object"""

    def serialize(self) -> bytes:
        return self.proto.SerializeToString()

    @classmethod
    def parse(cls, bytes_: ByteString):
        proto = cls._protobuf_class()
        proto.ParseFromString(bytes_)
        return cls.from_proto(proto)
