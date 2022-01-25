from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry_template import EntryTemplate
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryTemplatesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class EntryTemplatesPaginatedList:
    """  """

    _entry_templates: Union[Unset, List[EntryTemplate]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("entry_templates={}".format(repr(self._entry_templates)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "EntryTemplatesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry_templates: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._entry_templates, Unset):
            entry_templates = []
            for entry_templates_item_data in self._entry_templates:
                entry_templates_item = entry_templates_item_data.to_dict()

                entry_templates.append(entry_templates_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if entry_templates is not UNSET:
            field_dict["entryTemplates"] = entry_templates
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entry_templates() -> Union[Unset, List[EntryTemplate]]:
            entry_templates = []
            _entry_templates = d.pop("entryTemplates")
            for entry_templates_item_data in _entry_templates or []:
                entry_templates_item = EntryTemplate.from_dict(entry_templates_item_data)

                entry_templates.append(entry_templates_item)

            return entry_templates

        entry_templates = (
            get_entry_templates() if "entryTemplates" in d else cast(Union[Unset, List[EntryTemplate]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        entry_templates_paginated_list = cls(
            entry_templates=entry_templates,
            next_token=next_token,
        )

        return entry_templates_paginated_list

    @property
    def entry_templates(self) -> List[EntryTemplate]:
        if isinstance(self._entry_templates, Unset):
            raise NotPresentError(self, "entry_templates")
        return self._entry_templates

    @entry_templates.setter
    def entry_templates(self, value: List[EntryTemplate]) -> None:
        self._entry_templates = value

    @entry_templates.deleter
    def entry_templates(self) -> None:
        self._entry_templates = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
