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

T = TypeVar("T", bound="PoolV1PoolCoverageSummary")


@define(auto_attribs=True)
class PoolV1PoolCoverageSummary:
    """
    Attributes:
        covered (Union[Unset, bool]): If the CUSIP is covered by infima. Example: True.
        cusip (Union[Unset, str]): CUSIP of security. Example: True.
        reasons (Union[Unset, List[str]]): Array of reasons why the CUSIP is not covered. Example: ['31417EUD1'].
    """

    covered: Union[Unset, bool] = UNSET
    cusip: Union[Unset, str] = UNSET
    reasons: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        covered = self.covered
        cusip = self.cusip
        reasons: Union[Unset, List[str]] = UNSET
        if not isinstance(self.reasons, Unset):
            reasons = self.reasons

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if covered is not UNSET:
            field_dict["covered"] = covered
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if reasons is not UNSET:
            field_dict["reasons"] = reasons

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        covered = d.pop("covered", UNSET)

        cusip = d.pop("cusip", UNSET)

        reasons = cast(List[str], d.pop("reasons", UNSET))

        pool_v1_pool_coverage_summary = cls(
            covered=covered,
            cusip=cusip,
            reasons=reasons,
        )

        pool_v1_pool_coverage_summary.additional_properties = d
        return pool_v1_pool_coverage_summary

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
