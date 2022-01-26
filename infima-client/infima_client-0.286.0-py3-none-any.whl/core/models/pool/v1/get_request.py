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

from infima_client.core.models.core.factor_date import CoreFactorDate
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetRequest")


@define(auto_attribs=True)
class PoolV1GetRequest:
    """
    Attributes:
        cusips (List[str]): Pool CUSIPs to fetch Pool information. Example: 31417EUD1.
        factor_date (Union[Unset, CoreFactorDate]):
    """

    cusips: List[str]
    factor_date: Union[Unset, CoreFactorDate] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusips = self.cusips

        factor_date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.factor_date, Unset):
            factor_date = self.factor_date.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cusips": cusips,
            }
        )
        if factor_date is not UNSET:
            field_dict["factorDate"] = factor_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cusips = cast(List[str], d.pop("cusips"))

        _factor_date = d.pop("factorDate", UNSET)
        factor_date: Union[Unset, CoreFactorDate]
        if isinstance(_factor_date, Unset):
            factor_date = UNSET
        else:
            factor_date = CoreFactorDate.from_dict(_factor_date)

        pool_v1_get_request = cls(
            cusips=cusips,
            factor_date=factor_date,
        )

        pool_v1_get_request.additional_properties = d
        return pool_v1_get_request

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
