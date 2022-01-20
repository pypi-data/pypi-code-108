from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationCreate")


@attr.s(auto_attribs=True, repr=False)
class LocationCreate:
    """  """

    _name: str
    _schema_id: str
    _barcode: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _parent_storage_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("barcode={}".format(repr(self._barcode)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("parent_storage_id={}".format(repr(self._parent_storage_id)))
        return "LocationCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        schema_id = self._schema_id
        barcode = self._barcode
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        parent_storage_id = self._parent_storage_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "schemaId": schema_id,
            }
        )
        if barcode is not UNSET:
            field_dict["barcode"] = barcode
        if fields is not UNSET:
            field_dict["fields"] = fields
        if parent_storage_id is not UNSET:
            field_dict["parentStorageId"] = parent_storage_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_schema_id() -> str:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(str, UNSET)

        def get_barcode() -> Union[Unset, str]:
            barcode = d.pop("barcode")
            return barcode

        barcode = get_barcode() if "barcode" in d else cast(Union[Unset, str], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_parent_storage_id() -> Union[Unset, str]:
            parent_storage_id = d.pop("parentStorageId")
            return parent_storage_id

        parent_storage_id = (
            get_parent_storage_id() if "parentStorageId" in d else cast(Union[Unset, str], UNSET)
        )

        location_create = cls(
            name=name,
            schema_id=schema_id,
            barcode=barcode,
            fields=fields,
            parent_storage_id=parent_storage_id,
        )

        return location_create

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def schema_id(self) -> str:
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @property
    def barcode(self) -> str:
        if isinstance(self._barcode, Unset):
            raise NotPresentError(self, "barcode")
        return self._barcode

    @barcode.setter
    def barcode(self, value: str) -> None:
        self._barcode = value

    @barcode.deleter
    def barcode(self) -> None:
        self._barcode = UNSET

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
    def parent_storage_id(self) -> str:
        if isinstance(self._parent_storage_id, Unset):
            raise NotPresentError(self, "parent_storage_id")
        return self._parent_storage_id

    @parent_storage_id.setter
    def parent_storage_id(self, value: str) -> None:
        self._parent_storage_id = value

    @parent_storage_id.deleter
    def parent_storage_id(self) -> None:
        self._parent_storage_id = UNSET
