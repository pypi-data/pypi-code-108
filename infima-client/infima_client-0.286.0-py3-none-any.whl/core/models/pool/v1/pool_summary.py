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

from infima_client.core.models.pool.v1.occupancy_summary import PoolV1OccupancySummary
from infima_client.core.models.pool.v1.purpose_summary import PoolV1PurposeSummary
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1PoolSummary")


@define(auto_attribs=True)
class PoolV1PoolSummary:
    """Pool summary provides information about Purposes and Occupancy of the loans.

    Attributes:
        cusip (Union[Unset, str]):
        occupancy (Union[Unset, PoolV1OccupancySummary]): Loans occupancies composition between purchase and reFi.
        purpose (Union[Unset, PoolV1PurposeSummary]): Loans purposes composition between purchase and reFi.
    """

    cusip: Union[Unset, str] = UNSET
    occupancy: Union[Unset, PoolV1OccupancySummary] = UNSET
    purpose: Union[Unset, PoolV1PurposeSummary] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusip = self.cusip
        occupancy: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.occupancy, Unset):
            occupancy = self.occupancy.to_dict()

        purpose: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.purpose, Unset):
            purpose = self.purpose.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if occupancy is not UNSET:
            field_dict["occupancy"] = occupancy
        if purpose is not UNSET:
            field_dict["purpose"] = purpose

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cusip = d.pop("cusip", UNSET)

        _occupancy = d.pop("occupancy", UNSET)
        occupancy: Union[Unset, PoolV1OccupancySummary]
        if isinstance(_occupancy, Unset):
            occupancy = UNSET
        else:
            occupancy = PoolV1OccupancySummary.from_dict(_occupancy)

        _purpose = d.pop("purpose", UNSET)
        purpose: Union[Unset, PoolV1PurposeSummary]
        if isinstance(_purpose, Unset):
            purpose = UNSET
        else:
            purpose = PoolV1PurposeSummary.from_dict(_purpose)

        pool_v1_pool_summary = cls(
            cusip=cusip,
            occupancy=occupancy,
            purpose=purpose,
        )

        pool_v1_pool_summary.additional_properties = d
        return pool_v1_pool_summary

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
