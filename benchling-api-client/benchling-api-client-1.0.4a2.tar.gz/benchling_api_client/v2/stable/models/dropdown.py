from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.dropdown_option import DropdownOption
from ..types import UNSET, Unset

T = TypeVar("T", bound="Dropdown")


@attr.s(auto_attribs=True, repr=False)
class Dropdown:
    """ Dropdowns are registry-wide enums. Use dropdowns to standardize on spelling and naming conventions, especially for important metadata like resistance markers. """

    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _options: Union[Unset, List[DropdownOption]] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("options={}".format(repr(self._options)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Dropdown({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        options: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._options, Unset):
            options = []
            for options_item_data in self._options:
                options_item = options_item_data.to_dict()

                options.append(options_item)

        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if options is not UNSET:
            field_dict["options"] = options
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_archive_record() -> Union[Unset, None, ArchiveRecord]:
            archive_record = None
            _archive_record = d.pop("archiveRecord")
            if _archive_record is not None and not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecord.from_dict(_archive_record)

            return archive_record

        archive_record = (
            get_archive_record() if "archiveRecord" in d else cast(Union[Unset, None, ArchiveRecord], UNSET)
        )

        def get_options() -> Union[Unset, List[DropdownOption]]:
            options = []
            _options = d.pop("options")
            for options_item_data in _options or []:
                options_item = DropdownOption.from_dict(options_item_data)

                options.append(options_item)

            return options

        options = get_options() if "options" in d else cast(Union[Unset, List[DropdownOption]], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        dropdown = cls(
            archive_record=archive_record,
            options=options,
            id=id,
            name=name,
        )

        dropdown.additional_properties = d
        return dropdown

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
    def archive_record(self) -> Optional[ArchiveRecord]:
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: Optional[ArchiveRecord]) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET

    @property
    def options(self) -> List[DropdownOption]:
        """ Array of dropdown options """
        if isinstance(self._options, Unset):
            raise NotPresentError(self, "options")
        return self._options

    @options.setter
    def options(self, value: List[DropdownOption]) -> None:
        self._options = value

    @options.deleter
    def options(self) -> None:
        self._options = UNSET

    @property
    def id(self) -> str:
        """ ID of the dropdown """
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
    def name(self) -> str:
        """ Name of the dropdown """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
