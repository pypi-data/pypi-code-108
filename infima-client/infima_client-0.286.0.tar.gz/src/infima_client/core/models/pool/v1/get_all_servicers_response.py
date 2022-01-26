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

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetAllServicersResponse")


@define(auto_attribs=True)
class PoolV1GetAllServicersResponse:
    """
    Attributes:
        servicers (Union[Unset, List[str]]):
    """

    servicers: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        servicers: Union[Unset, List[str]] = UNSET
        if not isinstance(self.servicers, Unset):
            servicers = self.servicers

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if servicers is not UNSET:
            field_dict["servicers"] = servicers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        servicers = cast(List[str], d.pop("servicers", UNSET))

        pool_v1_get_all_servicers_response = cls(
            servicers=servicers,
        )

        pool_v1_get_all_servicers_response.additional_properties = d
        return pool_v1_get_all_servicers_response

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
