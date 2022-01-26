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

from infima_client.core.models.search.v0.saved_query import SearchV0SavedQuery
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0SaveQueryRequest")


@define(auto_attribs=True)
class SearchV0SaveQueryRequest:
    """
    Attributes:
        saved (Union[Unset, SearchV0SavedQuery]):
    """

    saved: Union[Unset, SearchV0SavedQuery] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        saved: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.saved, Unset):
            saved = self.saved.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if saved is not UNSET:
            field_dict["saved"] = saved

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _saved = d.pop("saved", UNSET)
        saved: Union[Unset, SearchV0SavedQuery]
        if isinstance(_saved, Unset):
            saved = UNSET
        else:
            saved = SearchV0SavedQuery.from_dict(_saved)

        search_v0_save_query_request = cls(
            saved=saved,
        )

        search_v0_save_query_request.additional_properties = d
        return search_v0_save_query_request

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
