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

from infima_client.core.models.pool.v1.pool_general_distributions_distributions import (
    PoolV1PoolGeneralDistributionsDistributions,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1PoolGeneralDistributions")


@define(auto_attribs=True)
class PoolV1PoolGeneralDistributions:
    """General pool Allocations

    Attributes:
        cusip (Union[Unset, str]):
        distributions (Union[Unset, PoolV1PoolGeneralDistributionsDistributions]):
    """

    cusip: Union[Unset, str] = UNSET
    distributions: Union[Unset, PoolV1PoolGeneralDistributionsDistributions] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusip = self.cusip
        distributions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.distributions, Unset):
            distributions = self.distributions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if distributions is not UNSET:
            field_dict["distributions"] = distributions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cusip = d.pop("cusip", UNSET)

        _distributions = d.pop("distributions", UNSET)
        distributions: Union[Unset, PoolV1PoolGeneralDistributionsDistributions]
        if isinstance(_distributions, Unset):
            distributions = UNSET
        else:
            distributions = PoolV1PoolGeneralDistributionsDistributions.from_dict(
                _distributions
            )

        pool_v1_pool_general_distributions = cls(
            cusip=cusip,
            distributions=distributions,
        )

        pool_v1_pool_general_distributions.additional_properties = d
        return pool_v1_pool_general_distributions

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
