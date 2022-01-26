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
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0Proportion")


@define(auto_attribs=True)
class SearchV0Proportion:
    """
    Attributes:
        max_proportion (Union[Unset, float]):
        min_proportion (Union[Unset, float]):
        name (Union[Unset, str]):
    """

    max_proportion: Union[Unset, float] = UNSET
    min_proportion: Union[Unset, float] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        max_proportion = self.max_proportion
        min_proportion = self.min_proportion
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_proportion is not UNSET:
            field_dict["maxProportion"] = max_proportion
        if min_proportion is not UNSET:
            field_dict["minProportion"] = min_proportion
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        max_proportion = d.pop("maxProportion", UNSET)

        min_proportion = d.pop("minProportion", UNSET)

        name = d.pop("name", UNSET)

        search_v0_proportion = cls(
            max_proportion=max_proportion,
            min_proportion=min_proportion,
            name=name,
        )

        search_v0_proportion.additional_properties = d
        return search_v0_proportion

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
