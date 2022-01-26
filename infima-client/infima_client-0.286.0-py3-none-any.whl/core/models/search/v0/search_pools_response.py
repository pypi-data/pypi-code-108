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

from infima_client.core.models.search.v0.search_pools_response_pools import (
    SearchV0SearchPoolsResponsePools,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0SearchPoolsResponse")


@define(auto_attribs=True)
class SearchV0SearchPoolsResponse:
    """
    Attributes:
        msg (Union[Unset, str]):
        pools (Union[Unset, SearchV0SearchPoolsResponsePools]):
    """

    msg: Union[Unset, str] = UNSET
    pools: Union[Unset, SearchV0SearchPoolsResponsePools] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        msg = self.msg
        pools: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pools, Unset):
            pools = self.pools.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if msg is not UNSET:
            field_dict["msg"] = msg
        if pools is not UNSET:
            field_dict["pools"] = pools

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        msg = d.pop("msg", UNSET)

        _pools = d.pop("pools", UNSET)
        pools: Union[Unset, SearchV0SearchPoolsResponsePools]
        if isinstance(_pools, Unset):
            pools = UNSET
        else:
            pools = SearchV0SearchPoolsResponsePools.from_dict(_pools)

        search_v0_search_pools_response = cls(
            msg=msg,
            pools=pools,
        )

        search_v0_search_pools_response.additional_properties = d
        return search_v0_search_pools_response

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
