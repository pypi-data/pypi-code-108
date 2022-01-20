from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry import Entry
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryById")


@attr.s(auto_attribs=True, repr=False)
class EntryById:
    """  """

    _entry: Union[Unset, Entry] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entry={}".format(repr(self._entry)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryById({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._entry, Unset):
            entry = self._entry.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entry is not UNSET:
            field_dict["entry"] = entry

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entry() -> Union[Unset, Entry]:
            entry: Union[Unset, Entry] = UNSET
            _entry = d.pop("entry")
            if not isinstance(_entry, Unset):
                entry = Entry.from_dict(_entry)

            return entry

        entry = get_entry() if "entry" in d else cast(Union[Unset, Entry], UNSET)

        entry_by_id = cls(
            entry=entry,
        )

        entry_by_id.additional_properties = d
        return entry_by_id

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
    def entry(self) -> Entry:
        """Entries are notes that users can take. They're organized by "days" (which are user-configurable) and modeled within each day as a list of "notes." Each note has a type - the simplest is a "text" type, but lists, tables, and external files are also supported.

        *Note:* the current Entry resource has a few limitations:
        - Formatting information is not yet supported. Header formatting, bolding, and other stylistic information is not presented.
        - Data in tables is presented as text always - numeric values will need to be parsed into floats or integers, as appropriate.

        Note: Data in Results tables are not accessible through this API call. Results table data can be called through the Results API calls.
        """
        if isinstance(self._entry, Unset):
            raise NotPresentError(self, "entry")
        return self._entry

    @entry.setter
    def entry(self, value: Entry) -> None:
        self._entry = value

    @entry.deleter
    def entry(self) -> None:
        self._entry = UNSET
