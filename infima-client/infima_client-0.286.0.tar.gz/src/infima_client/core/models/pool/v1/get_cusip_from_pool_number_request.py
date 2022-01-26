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
    cast,
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetCusipFromPoolNumberRequest")


@define(auto_attribs=True)
class PoolV1GetCusipFromPoolNumberRequest:
    """
    Attributes:
        pool_numbers (List[str]):
    """

    pool_numbers: List[str]
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pool_numbers = self.pool_numbers

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "poolNumbers": pool_numbers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pool_numbers = cast(List[str], d.pop("poolNumbers"))

        pool_v1_get_cusip_from_pool_number_request = cls(
            pool_numbers=pool_numbers,
        )

        pool_v1_get_cusip_from_pool_number_request.additional_properties = d
        return pool_v1_get_cusip_from_pool_number_request

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
