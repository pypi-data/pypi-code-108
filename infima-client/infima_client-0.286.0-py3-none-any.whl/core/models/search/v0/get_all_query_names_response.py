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

T = TypeVar("T", bound="SearchV0GetAllQueryNamesResponse")


@define(auto_attribs=True)
class SearchV0GetAllQueryNamesResponse:
    """
    Attributes:
        names (Union[Unset, List[str]]):
    """

    names: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        names: Union[Unset, List[str]] = UNSET
        if not isinstance(self.names, Unset):
            names = self.names

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if names is not UNSET:
            field_dict["names"] = names

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        names = cast(List[str], d.pop("names", UNSET))

        search_v0_get_all_query_names_response = cls(
            names=names,
        )

        search_v0_get_all_query_names_response.additional_properties = d
        return search_v0_get_all_query_names_response

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
