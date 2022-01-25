from abc import abstractmethod
from dataclasses import dataclass
from typing import Type, TypeVar, Generic, Optional


@dataclass
class Serializable:
    """
    Base class for dataclasses that can be serialized and deserialized.
    Subclasses must be defined as dataclasses.
    """
    pass


TSerializable = TypeVar('TSerializable', bound=Serializable)
TSerialized = TypeVar('TSerialized')


class Serializer(Generic[TSerialized]):
    """
    An interface for serializing and deserializing dataclasses.
    """

    @abstractmethod
    def serialize(
            self,
            obj: TSerializable,
            schema: Optional[Type[TSerializable]] = None,
    ) -> TSerialized:
        """
        Serialize an object.
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize(
            self,
            data: TSerialized,
            schema: Type[TSerializable],
            validate: bool = True,
    ) -> TSerializable:
        """
        Deserialize an object.
        """
        raise NotImplementedError
