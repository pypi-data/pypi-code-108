from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..models.plate_create_wells import PlateCreateWells
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlateCreate")


@attr.s(auto_attribs=True, repr=False)
class PlateCreate:
    """  """

    _schema_id: str
    _barcode: Union[Unset, str] = UNSET
    _container_schema_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _name: Union[Unset, str] = UNSET
    _parent_storage_id: Union[Unset, str] = UNSET
    _project_id: Union[Unset, str] = UNSET
    _wells: Union[Unset, PlateCreateWells] = UNSET

    def __repr__(self):
        fields = []
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("barcode={}".format(repr(self._barcode)))
        fields.append("container_schema_id={}".format(repr(self._container_schema_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("parent_storage_id={}".format(repr(self._parent_storage_id)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("wells={}".format(repr(self._wells)))
        return "PlateCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        schema_id = self._schema_id
        barcode = self._barcode
        container_schema_id = self._container_schema_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        name = self._name
        parent_storage_id = self._parent_storage_id
        project_id = self._project_id
        wells: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._wells, Unset):
            wells = self._wells.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "schemaId": schema_id,
            }
        )
        if barcode is not UNSET:
            field_dict["barcode"] = barcode
        if container_schema_id is not UNSET:
            field_dict["containerSchemaId"] = container_schema_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if name is not UNSET:
            field_dict["name"] = name
        if parent_storage_id is not UNSET:
            field_dict["parentStorageId"] = parent_storage_id
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if wells is not UNSET:
            field_dict["wells"] = wells

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_schema_id() -> str:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(str, UNSET)

        def get_barcode() -> Union[Unset, str]:
            barcode = d.pop("barcode")
            return barcode

        barcode = get_barcode() if "barcode" in d else cast(Union[Unset, str], UNSET)

        def get_container_schema_id() -> Union[Unset, str]:
            container_schema_id = d.pop("containerSchemaId")
            return container_schema_id

        container_schema_id = (
            get_container_schema_id() if "containerSchemaId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_parent_storage_id() -> Union[Unset, str]:
            parent_storage_id = d.pop("parentStorageId")
            return parent_storage_id

        parent_storage_id = (
            get_parent_storage_id() if "parentStorageId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_project_id() -> Union[Unset, str]:
            project_id = d.pop("projectId")
            return project_id

        project_id = get_project_id() if "projectId" in d else cast(Union[Unset, str], UNSET)

        def get_wells() -> Union[Unset, PlateCreateWells]:
            wells: Union[Unset, PlateCreateWells] = UNSET
            _wells = d.pop("wells")
            if not isinstance(_wells, Unset):
                wells = PlateCreateWells.from_dict(_wells)

            return wells

        wells = get_wells() if "wells" in d else cast(Union[Unset, PlateCreateWells], UNSET)

        plate_create = cls(
            schema_id=schema_id,
            barcode=barcode,
            container_schema_id=container_schema_id,
            fields=fields,
            name=name,
            parent_storage_id=parent_storage_id,
            project_id=project_id,
            wells=wells,
        )

        return plate_create

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
    def container_schema_id(self) -> str:
        if isinstance(self._container_schema_id, Unset):
            raise NotPresentError(self, "container_schema_id")
        return self._container_schema_id

    @container_schema_id.setter
    def container_schema_id(self, value: str) -> None:
        self._container_schema_id = value

    @container_schema_id.deleter
    def container_schema_id(self) -> None:
        self._container_schema_id = UNSET

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
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

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

    @property
    def project_id(self) -> str:
        if isinstance(self._project_id, Unset):
            raise NotPresentError(self, "project_id")
        return self._project_id

    @project_id.setter
    def project_id(self, value: str) -> None:
        self._project_id = value

    @project_id.deleter
    def project_id(self) -> None:
        self._project_id = UNSET

    @property
    def wells(self) -> PlateCreateWells:
        if isinstance(self._wells, Unset):
            raise NotPresentError(self, "wells")
        return self._wells

    @wells.setter
    def wells(self, value: PlateCreateWells) -> None:
        self._wells = value

    @wells.deleter
    def wells(self) -> None:
        self._wells = UNSET
