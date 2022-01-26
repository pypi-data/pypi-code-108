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

from infima_client.core.models.pool.v1.pool_geographic_distribution_states import (
    PoolV1PoolGeographicDistributionStates,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1PoolGeographicDistribution")


@define(auto_attribs=True)
class PoolV1PoolGeographicDistribution:
    """Pool State Geographical Distribution.

    Attributes:
        cusip (Union[Unset, str]):
        states (Union[Unset, PoolV1PoolGeographicDistributionStates]): Array of state allocations.
    """

    cusip: Union[Unset, str] = UNSET
    states: Union[Unset, PoolV1PoolGeographicDistributionStates] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusip = self.cusip
        states: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.states, Unset):
            states = self.states.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if states is not UNSET:
            field_dict["states"] = states

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cusip = d.pop("cusip", UNSET)

        _states = d.pop("states", UNSET)
        states: Union[Unset, PoolV1PoolGeographicDistributionStates]
        if isinstance(_states, Unset):
            states = UNSET
        else:
            states = PoolV1PoolGeographicDistributionStates.from_dict(_states)

        pool_v1_pool_geographic_distribution = cls(
            cusip=cusip,
            states=states,
        )

        pool_v1_pool_geographic_distribution.additional_properties = d
        return pool_v1_pool_geographic_distribution

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
