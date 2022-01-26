from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from attr import define, field

from infima_client.core.models.google.protobuf.any import GoogleProtobufAny
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="GoogleRpcStatus")


@define(auto_attribs=True)
class GoogleRpcStatus:
    """
    Attributes:
        code (Union[Unset, int]):
        details (Union[Unset, List[GoogleProtobufAny]]):
        message (Union[Unset, str]):
    """

    code: Union[Unset, int] = UNSET
    details: Union[Unset, List[GoogleProtobufAny]] = UNSET
    message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        code = self.code
        details: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.details, Unset):
            details = []
            for details_item_data in self.details:
                details_item = details_item_data.to_dict()

                details.append(details_item)

        message = self.message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if details is not UNSET:
            field_dict["details"] = details
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        code = d.pop("code", UNSET)

        details = []
        _details = d.pop("details", UNSET)
        for details_item_data in _details or []:
            details_item = GoogleProtobufAny.from_dict(details_item_data)

            details.append(details_item)

        message = d.pop("message", UNSET)

        google_rpc_status = cls(
            code=code,
            details=details,
            message=message,
        )

        google_rpc_status.additional_properties = d
        return google_rpc_status

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
