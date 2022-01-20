from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.custom_fields import CustomFields
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryCreate")


@attr.s(auto_attribs=True, repr=False)
class EntryCreate:
    """  """

    _folder_id: str
    _name: str
    _author_ids: Union[Unset, str] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _entry_template_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _schema_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("author_ids={}".format(repr(self._author_ids)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("entry_template_id={}".format(repr(self._entry_template_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        return "EntryCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        folder_id = self._folder_id
        name = self._name
        author_ids = self._author_ids
        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        entry_template_id = self._entry_template_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        schema_id = self._schema_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "folderId": folder_id,
                "name": name,
            }
        )
        if author_ids is not UNSET:
            field_dict["authorIds"] = author_ids
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if entry_template_id is not UNSET:
            field_dict["entryTemplateId"] = entry_template_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if schema_id is not UNSET:
            field_dict["schemaId"] = schema_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_folder_id() -> str:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(str, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_author_ids() -> Union[Unset, str]:
            author_ids = d.pop("authorIds")
            return author_ids

        author_ids = get_author_ids() if "authorIds" in d else cast(Union[Unset, str], UNSET)

        def get_custom_fields() -> Union[Unset, CustomFields]:
            custom_fields: Union[Unset, CustomFields] = UNSET
            _custom_fields = d.pop("customFields")
            if not isinstance(_custom_fields, Unset):
                custom_fields = CustomFields.from_dict(_custom_fields)

            return custom_fields

        custom_fields = (
            get_custom_fields() if "customFields" in d else cast(Union[Unset, CustomFields], UNSET)
        )

        def get_entry_template_id() -> Union[Unset, str]:
            entry_template_id = d.pop("entryTemplateId")
            return entry_template_id

        entry_template_id = (
            get_entry_template_id() if "entryTemplateId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_schema_id() -> Union[Unset, str]:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(Union[Unset, str], UNSET)

        entry_create = cls(
            folder_id=folder_id,
            name=name,
            author_ids=author_ids,
            custom_fields=custom_fields,
            entry_template_id=entry_template_id,
            fields=fields,
            schema_id=schema_id,
        )

        return entry_create

    @property
    def folder_id(self) -> str:
        """ ID of the folder that will contain the entry """
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value

    @property
    def name(self) -> str:
        """ Name of the entry """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def author_ids(self) -> str:
        """IDs of users to set as the entry's authors. Defaults to the creator."""
        if isinstance(self._author_ids, Unset):
            raise NotPresentError(self, "author_ids")
        return self._author_ids

    @author_ids.setter
    def author_ids(self, value: str) -> None:
        self._author_ids = value

    @author_ids.deleter
    def author_ids(self) -> None:
        self._author_ids = UNSET

    @property
    def custom_fields(self) -> CustomFields:
        if isinstance(self._custom_fields, Unset):
            raise NotPresentError(self, "custom_fields")
        return self._custom_fields

    @custom_fields.setter
    def custom_fields(self, value: CustomFields) -> None:
        self._custom_fields = value

    @custom_fields.deleter
    def custom_fields(self) -> None:
        self._custom_fields = UNSET

    @property
    def entry_template_id(self) -> str:
        """ ID of the template to clone the entry from """
        if isinstance(self._entry_template_id, Unset):
            raise NotPresentError(self, "entry_template_id")
        return self._entry_template_id

    @entry_template_id.setter
    def entry_template_id(self, value: str) -> None:
        self._entry_template_id = value

    @entry_template_id.deleter
    def entry_template_id(self) -> None:
        self._entry_template_id = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def schema_id(self) -> str:
        """ ID of the entry's schema """
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @schema_id.deleter
    def schema_id(self) -> None:
        self._schema_id = UNSET
