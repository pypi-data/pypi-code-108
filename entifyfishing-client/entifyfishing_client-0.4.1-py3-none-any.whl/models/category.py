from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Category")


@attr.s(auto_attribs=True)
class Category:
    """ """

    category: str
    source: Union[Unset, str] = UNSET
    weight: Union[Unset, float] = UNSET
    page_id: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        category = self.category
        source = self.source
        weight = self.weight
        page_id = self.page_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "category": category,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source
        if weight is not UNSET:
            field_dict["weight"] = weight
        if page_id is not UNSET:
            field_dict["page_id"] = page_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        category = d.pop("category")

        source = d.pop("source", UNSET)

        weight = d.pop("weight", UNSET)

        page_id = d.pop("page_id", UNSET)

        category = cls(
            category=category,
            source=source,
            weight=weight,
            page_id=page_id,
        )

        return category
