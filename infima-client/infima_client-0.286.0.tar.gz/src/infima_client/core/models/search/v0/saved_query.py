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

from infima_client.core.models.search.v0.search_pools_request import (
    SearchV0SearchPoolsRequest,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0SavedQuery")


@define(auto_attribs=True)
class SearchV0SavedQuery:
    """
    Attributes:
        name (Union[Unset, str]):
        query (Union[Unset, SearchV0SearchPoolsRequest]):
    """

    name: Union[Unset, str] = UNSET
    query: Union[Unset, SearchV0SearchPoolsRequest] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        query: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.query, Unset):
            query = self.query.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if query is not UNSET:
            field_dict["query"] = query

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        _query = d.pop("query", UNSET)
        query: Union[Unset, SearchV0SearchPoolsRequest]
        if isinstance(_query, Unset):
            query = UNSET
        else:
            query = SearchV0SearchPoolsRequest.from_dict(_query)

        search_v0_saved_query = cls(
            name=name,
            query=query,
        )

        search_v0_saved_query.additional_properties = d
        return search_v0_saved_query

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
