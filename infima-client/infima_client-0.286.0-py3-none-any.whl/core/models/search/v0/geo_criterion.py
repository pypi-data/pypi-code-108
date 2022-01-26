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

from infima_client.core.models.search.v0.proportion import SearchV0Proportion
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0GeoCriterion")


@define(auto_attribs=True)
class SearchV0GeoCriterion:
    """
    Attributes:
        excludes (Union[Unset, List[SearchV0Proportion]]):
        includes (Union[Unset, List[SearchV0Proportion]]):
    """

    excludes: Union[Unset, List[SearchV0Proportion]] = UNSET
    includes: Union[Unset, List[SearchV0Proportion]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        excludes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.excludes, Unset):
            excludes = []
            for excludes_item_data in self.excludes:
                excludes_item = excludes_item_data.to_dict()

                excludes.append(excludes_item)

        includes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.includes, Unset):
            includes = []
            for includes_item_data in self.includes:
                includes_item = includes_item_data.to_dict()

                includes.append(includes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if excludes is not UNSET:
            field_dict["excludes"] = excludes
        if includes is not UNSET:
            field_dict["includes"] = includes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        excludes = []
        _excludes = d.pop("excludes", UNSET)
        for excludes_item_data in _excludes or []:
            excludes_item = SearchV0Proportion.from_dict(excludes_item_data)

            excludes.append(excludes_item)

        includes = []
        _includes = d.pop("includes", UNSET)
        for includes_item_data in _includes or []:
            includes_item = SearchV0Proportion.from_dict(includes_item_data)

            includes.append(includes_item)

        search_v0_geo_criterion = cls(
            excludes=excludes,
            includes=includes,
        )

        search_v0_geo_criterion.additional_properties = d
        return search_v0_geo_criterion

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
