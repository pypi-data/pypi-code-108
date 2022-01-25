from abc import ABC, abstractmethod
from typing import Type


# The following helper class ProtobufParser is used to convert a Union of Terality ProtobufWrapper types to protobuf.
# As opposed to methods `proto` and `to_proto` that manipulate ProtobufWrappers, the methods under ProtobufConverter
# manipulate Unions of ProtobufWrapper.
# i.e. FileRead = Union[FileReadLocal, FileReadS3] FileRead itself is not a ProtobufWrapper


class ProtobufParser(ABC):
    """Converts Union[ProtobufWrapper, ProtobufWrapper, ...] objects to bytes and vice-versa"""

    protobuf_class: Type

    @classmethod
    @abstractmethod
    def to_protobuf_message(cls, terality_obj):
        pass

    @classmethod
    @abstractmethod
    def to_terality_class(cls, proto):
        pass

    @classmethod
    def serialize(cls, terality_obj) -> bytes:
        proto = cls.to_protobuf_message(terality_obj)
        return proto.SerializeToString()

    @classmethod
    def parse(cls, bytes_: bytes):
        proto = cls.protobuf_class()
        proto.ParseFromString(bytes_)
        return cls.to_terality_class(proto)
