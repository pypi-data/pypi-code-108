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
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1OccupancySummary")


@define(auto_attribs=True)
class PoolV1OccupancySummary:
    """Loans occupancies composition between purchase and reFi.

    Attributes:
        percentage_investor (Union[Unset, float]): Proportion of investors.
        percentage_owner (Union[Unset, float]): Proportion of first home owners.
        percentage_second_home (Union[Unset, float]): Proportion of second home owners.
    """

    percentage_investor: Union[Unset, float] = UNSET
    percentage_owner: Union[Unset, float] = UNSET
    percentage_second_home: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        percentage_investor = self.percentage_investor
        percentage_owner = self.percentage_owner
        percentage_second_home = self.percentage_second_home

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if percentage_investor is not UNSET:
            field_dict["percentageInvestor"] = percentage_investor
        if percentage_owner is not UNSET:
            field_dict["percentageOwner"] = percentage_owner
        if percentage_second_home is not UNSET:
            field_dict["percentageSecondHome"] = percentage_second_home

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        percentage_investor = d.pop("percentageInvestor", UNSET)

        percentage_owner = d.pop("percentageOwner", UNSET)

        percentage_second_home = d.pop("percentageSecondHome", UNSET)

        pool_v1_occupancy_summary = cls(
            percentage_investor=percentage_investor,
            percentage_owner=percentage_owner,
            percentage_second_home=percentage_second_home,
        )

        pool_v1_occupancy_summary.additional_properties = d
        return pool_v1_occupancy_summary

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
