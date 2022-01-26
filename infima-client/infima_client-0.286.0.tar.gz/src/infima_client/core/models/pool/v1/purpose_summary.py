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

T = TypeVar("T", bound="PoolV1PurposeSummary")


@define(auto_attribs=True)
class PoolV1PurposeSummary:
    """Loans purposes composition between purchase and reFi.

    Attributes:
        percentage_purchase (Union[Unset, float]): Proportion of purchases.
        percentage_refi (Union[Unset, float]): Proportion of refinances.
    """

    percentage_purchase: Union[Unset, float] = UNSET
    percentage_refi: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        percentage_purchase = self.percentage_purchase
        percentage_refi = self.percentage_refi

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if percentage_purchase is not UNSET:
            field_dict["percentagePurchase"] = percentage_purchase
        if percentage_refi is not UNSET:
            field_dict["percentageRefi"] = percentage_refi

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        percentage_purchase = d.pop("percentagePurchase", UNSET)

        percentage_refi = d.pop("percentageRefi", UNSET)

        pool_v1_purpose_summary = cls(
            percentage_purchase=percentage_purchase,
            percentage_refi=percentage_refi,
        )

        pool_v1_purpose_summary.additional_properties = d
        return pool_v1_purpose_summary

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
