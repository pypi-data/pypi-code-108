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

from infima_client.core.models.pool.v1.get_cusip_from_pool_number_response_cusips import (
    PoolV1GetCusipFromPoolNumberResponseCusips,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetCusipFromPoolNumberResponse")


@define(auto_attribs=True)
class PoolV1GetCusipFromPoolNumberResponse:
    """
    Attributes:
        cusips (Union[Unset, PoolV1GetCusipFromPoolNumberResponseCusips]):
    """

    cusips: Union[Unset, PoolV1GetCusipFromPoolNumberResponseCusips] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusips: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cusips, Unset):
            cusips = self.cusips.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cusips is not UNSET:
            field_dict["cusips"] = cusips

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _cusips = d.pop("cusips", UNSET)
        cusips: Union[Unset, PoolV1GetCusipFromPoolNumberResponseCusips]
        if isinstance(_cusips, Unset):
            cusips = UNSET
        else:
            cusips = PoolV1GetCusipFromPoolNumberResponseCusips.from_dict(_cusips)

        pool_v1_get_cusip_from_pool_number_response = cls(
            cusips=cusips,
        )

        pool_v1_get_cusip_from_pool_number_response.additional_properties = d
        return pool_v1_get_cusip_from_pool_number_response

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
