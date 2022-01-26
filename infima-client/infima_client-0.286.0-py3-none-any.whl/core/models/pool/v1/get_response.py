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

from infima_client.core.models.pool.v1.get_response_pools import PoolV1GetResponsePools
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetResponse")


@define(auto_attribs=True)
class PoolV1GetResponse:
    """
    Attributes:
        pools (Union[Unset, PoolV1GetResponsePools]): Mapping of CUSIP to pool object.
    """

    pools: Union[Unset, PoolV1GetResponsePools] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pools: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pools, Unset):
            pools = self.pools.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pools is not UNSET:
            field_dict["pools"] = pools

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _pools = d.pop("pools", UNSET)
        pools: Union[Unset, PoolV1GetResponsePools]
        if isinstance(_pools, Unset):
            pools = UNSET
        else:
            pools = PoolV1GetResponsePools.from_dict(_pools)

        pool_v1_get_response = cls(
            pools=pools,
        )

        pool_v1_get_response.additional_properties = d
        return pool_v1_get_response

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
