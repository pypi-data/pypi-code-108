from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry_link import EntryLink
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryTableCell")


@attr.s(auto_attribs=True, repr=False)
class EntryTableCell:
    """  """

    _link: Union[Unset, EntryLink] = UNSET
    _text: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("link={}".format(repr(self._link)))
        fields.append("text={}".format(repr(self._text)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryTableCell({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        link: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._link, Unset):
            link = self._link.to_dict()

        text = self._text

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if link is not UNSET:
            field_dict["link"] = link
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_link() -> Union[Unset, EntryLink]:
            link: Union[Unset, EntryLink] = UNSET
            _link = d.pop("link")
            if not isinstance(_link, Unset):
                link = EntryLink.from_dict(_link)

            return link

        link = get_link() if "link" in d else cast(Union[Unset, EntryLink], UNSET)

        def get_text() -> Union[Unset, str]:
            text = d.pop("text")
            return text

        text = get_text() if "text" in d else cast(Union[Unset, str], UNSET)

        entry_table_cell = cls(
            link=link,
            text=text,
        )

        entry_table_cell.additional_properties = d
        return entry_table_cell

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def link(self) -> EntryLink:
        """Links are contained within notes to reference resources that live outside of the entry. A link can target an external resource via an http(s):// hyperlink or a Benchling resource via @-mentions and drag-n-drop."""
        if isinstance(self._link, Unset):
            raise NotPresentError(self, "link")
        return self._link

    @link.setter
    def link(self, value: EntryLink) -> None:
        self._link = value

    @link.deleter
    def link(self) -> None:
        self._link = UNSET

    @property
    def text(self) -> str:
        """The textual content of the cell. If the cell was originally a formula, this will be the evaluated version of the formula."""
        if isinstance(self._text, Unset):
            raise NotPresentError(self, "text")
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @text.deleter
    def text(self) -> None:
        self._text = UNSET
