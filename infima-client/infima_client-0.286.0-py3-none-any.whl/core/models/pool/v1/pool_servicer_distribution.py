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

from infima_client.core.models.pool.v1.pool_servicer_distribution_servicers import (
    PoolV1PoolServicerDistributionServicers,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1PoolServicerDistribution")


@define(auto_attribs=True)
class PoolV1PoolServicerDistribution:
    """Pool Servicers allocations.

    Attributes:
        cusip (Union[Unset, str]):
        servicers (Union[Unset, PoolV1PoolServicerDistributionServicers]): Array of servicers allocations.
    """

    cusip: Union[Unset, str] = UNSET
    servicers: Union[Unset, PoolV1PoolServicerDistributionServicers] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusip = self.cusip
        servicers: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.servicers, Unset):
            servicers = self.servicers.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if servicers is not UNSET:
            field_dict["servicers"] = servicers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cusip = d.pop("cusip", UNSET)

        _servicers = d.pop("servicers", UNSET)
        servicers: Union[Unset, PoolV1PoolServicerDistributionServicers]
        if isinstance(_servicers, Unset):
            servicers = UNSET
        else:
            servicers = PoolV1PoolServicerDistributionServicers.from_dict(_servicers)

        pool_v1_pool_servicer_distribution = cls(
            cusip=cusip,
            servicers=servicers,
        )

        pool_v1_pool_servicer_distribution.additional_properties = d
        return pool_v1_pool_servicer_distribution

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
