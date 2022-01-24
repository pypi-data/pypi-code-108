from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="Page")


@attr.s(auto_attribs=True)
class Page:
    """ """

    page_height: float
    page_width: float
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        page_height = self.page_height
        page_width = self.page_width

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page_height": page_height,
                "page_width": page_width,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        page_height = d.pop("page_height")

        page_width = d.pop("page_width")

        page = cls(
            page_height=page_height,
            page_width=page_width,
        )

        page.additional_properties = d
        return page

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
