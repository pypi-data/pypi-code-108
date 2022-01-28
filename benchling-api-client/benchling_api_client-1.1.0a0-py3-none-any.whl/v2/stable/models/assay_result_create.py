from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.assay_fields_create import AssayFieldsCreate
from ..models.assay_result_create_field_validation import AssayResultCreateFieldValidation
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultCreate")


@attr.s(auto_attribs=True, repr=False)
class AssayResultCreate:
    """  """

    _fields: Union[Fields, AssayFieldsCreate, UnknownType]
    _schema_id: str
    _field_validation: Union[Unset, AssayResultCreateFieldValidation] = UNSET
    _id: Union[Unset, str] = UNSET
    _project_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("field_validation={}".format(repr(self._field_validation)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayResultCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        if isinstance(self._fields, UnknownType):
            fields = self._fields.value
        elif isinstance(self._fields, Fields):
            fields = self._fields.to_dict()

        else:
            fields = self._fields.to_dict()

        schema_id = self._schema_id
        field_validation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._field_validation, Unset):
            field_validation = self._field_validation.to_dict()

        id = self._id
        project_id = self._project_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fields": fields,
                "schemaId": schema_id,
            }
        )
        if field_validation is not UNSET:
            field_dict["fieldValidation"] = field_validation
        if id is not UNSET:
            field_dict["id"] = id
        if project_id is not UNSET:
            field_dict["projectId"] = project_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_fields() -> Union[Fields, AssayFieldsCreate, UnknownType]:
            def _parse_fields(data: Union[Dict[str, Any]]) -> Union[Fields, AssayFieldsCreate, UnknownType]:
                fields: Union[Fields, AssayFieldsCreate, UnknownType]
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    fields = Fields.from_dict(data)

                    return fields
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    fields = AssayFieldsCreate.from_dict(data)

                    return fields
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            fields = _parse_fields(d.pop("fields"))

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Fields, AssayFieldsCreate, UnknownType], UNSET)

        def get_schema_id() -> str:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(str, UNSET)

        def get_field_validation() -> Union[Unset, AssayResultCreateFieldValidation]:
            field_validation: Union[Unset, AssayResultCreateFieldValidation] = UNSET
            _field_validation = d.pop("fieldValidation")
            if not isinstance(_field_validation, Unset):
                field_validation = AssayResultCreateFieldValidation.from_dict(_field_validation)

            return field_validation

        field_validation = (
            get_field_validation()
            if "fieldValidation" in d
            else cast(Union[Unset, AssayResultCreateFieldValidation], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_project_id() -> Union[Unset, None, str]:
            project_id = d.pop("projectId")
            return project_id

        project_id = get_project_id() if "projectId" in d else cast(Union[Unset, None, str], UNSET)

        assay_result_create = cls(
            fields=fields,
            schema_id=schema_id,
            field_validation=field_validation,
            id=id,
            project_id=project_id,
        )

        assay_result_create.additional_properties = d
        return assay_result_create

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
    def fields(self) -> Union[Fields, AssayFieldsCreate, UnknownType]:
        """ Dictionary of result fields """
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Union[Fields, AssayFieldsCreate, UnknownType]) -> None:
        self._fields = value

    @property
    def schema_id(self) -> str:
        """ ID of result schema under which to upload this result """
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @property
    def field_validation(self) -> AssayResultCreateFieldValidation:
        """Dictionary mapping field names to UserValidation Resources."""
        if isinstance(self._field_validation, Unset):
            raise NotPresentError(self, "field_validation")
        return self._field_validation

    @field_validation.setter
    def field_validation(self, value: AssayResultCreateFieldValidation) -> None:
        self._field_validation = value

    @field_validation.deleter
    def field_validation(self) -> None:
        self._field_validation = UNSET

    @property
    def id(self) -> str:
        """ UUID """
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
    def project_id(self) -> Optional[str]:
        """The project that the assay result should be uploaded to. Only users with read access to the project will be able to read the assay result. Leaving this empty will result in only the creator having read access."""
        if isinstance(self._project_id, Unset):
            raise NotPresentError(self, "project_id")
        return self._project_id

    @project_id.setter
    def project_id(self, value: Optional[str]) -> None:
        self._project_id = value

    @project_id.deleter
    def project_id(self) -> None:
        self._project_id = UNSET
