from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar, Union

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="GoogleProtobufAny")


@define(auto_attribs=True)
class GoogleProtobufAny:
    """
    Attributes:
        type (Union[Unset, str]):
    """

    type: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if type is not UNSET:
            field_dict["@type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("@type", UNSET)

        google_protobuf_any = cls(
            type=type,
        )

        return google_protobuf_any
