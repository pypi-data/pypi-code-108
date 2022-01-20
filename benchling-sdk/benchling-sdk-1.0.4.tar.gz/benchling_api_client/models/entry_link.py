from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry_link_type import EntryLinkType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryLink")


@attr.s(auto_attribs=True, repr=False)
class EntryLink:
    """Links are contained within notes to reference resources that live outside of the entry. A link can target an external resource via an http(s):// hyperlink or a Benchling resource via @-mentions and drag-n-drop."""

    _id: Union[Unset, str] = UNSET
    _type: Union[Unset, EntryLinkType] = UNSET
    _web_url: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryLink({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        web_url = self._web_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["type"] = type
        if web_url is not UNSET:
            field_dict["webURL"] = web_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, EntryLinkType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = EntryLinkType(_type)
                except ValueError:
                    type = EntryLinkType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, EntryLinkType], UNSET)

        def get_web_url() -> Union[Unset, None, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, None, str], UNSET)

        entry_link = cls(
            id=id,
            type=type,
            web_url=web_url,
        )

        entry_link.additional_properties = d
        return entry_link

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
    def id(self) -> str:
        """For linked Benchling resources, this will be the ID of that resource (e.g., 'seq_RhYGVnHF'). Omitted for "link" types."""
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def type(self) -> EntryLinkType:
        """The type of resource being linked. For hyperlinks: 'link'. For linked Benchling resources, one of: 'user', 'request', 'entry', 'stage_entry', 'protocol', 'workflow', 'custom_entity', 'aa_sequence', 'dna_sequence', 'batch', 'box', 'container', 'location', 'plate'."""
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: EntryLinkType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def web_url(self) -> Optional[str]:
        """Canonical URL of the linked Benchling resource (if you have at least READ authorization for that resource), or the explicit URL provided as hyperlink for "link" types. Note: locations do not currently have a URL."""
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: Optional[str]) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET
