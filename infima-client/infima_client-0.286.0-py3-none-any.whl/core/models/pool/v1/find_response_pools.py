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

from infima_client.core.models.pool.v1.pool import PoolV1Pool
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1FindResponsePools")


@define(auto_attribs=True)
class PoolV1FindResponsePools:
    """Mapping of CUSIP to pool object."""

    additional_properties: Dict[str, PoolV1Pool] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pool_v1_find_response_pools = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = PoolV1Pool.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        pool_v1_find_response_pools.additional_properties = additional_properties
        return pool_v1_find_response_pools

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> PoolV1Pool:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: PoolV1Pool) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
