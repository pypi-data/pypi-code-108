from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.assay_fields_create import AssayFieldsCreate
from ..models.assay_run_validation_status import AssayRunValidationStatus
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayRunCreate")


@attr.s(auto_attribs=True, repr=False)
class AssayRunCreate:
    """  """

    _fields: Union[Fields, AssayFieldsCreate, UnknownType]
    _schema_id: str
    _id: Union[Unset, str] = UNSET
    _project_id: Union[Unset, str] = UNSET
    _validation_comment: Union[Unset, str] = UNSET
    _validation_status: Union[Unset, AssayRunValidationStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("validation_comment={}".format(repr(self._validation_comment)))
        fields.append("validation_status={}".format(repr(self._validation_status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayRunCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        if isinstance(self._fields, UnknownType):
            fields = self._fields.value
        elif isinstance(self._fields, Fields):
            fields = self._fields.to_dict()

        else:
            fields = self._fields.to_dict()

        schema_id = self._schema_id
        id = self._id
        project_id = self._project_id
        validation_comment = self._validation_comment
        validation_status: Union[Unset, int] = UNSET
        if not isinstance(self._validation_status, Unset):
            validation_status = self._validation_status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fields": fields,
                "schemaId": schema_id,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if validation_comment is not UNSET:
            field_dict["validationComment"] = validation_comment
        if validation_status is not UNSET:
            field_dict["validationStatus"] = validation_status

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

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_project_id() -> Union[Unset, str]:
            project_id = d.pop("projectId")
            return project_id

        project_id = get_project_id() if "projectId" in d else cast(Union[Unset, str], UNSET)

        def get_validation_comment() -> Union[Unset, str]:
            validation_comment = d.pop("validationComment")
            return validation_comment

        validation_comment = (
            get_validation_comment() if "validationComment" in d else cast(Union[Unset, str], UNSET)
        )

        def get_validation_status() -> Union[Unset, AssayRunValidationStatus]:
            validation_status = None
            _validation_status = d.pop("validationStatus")
            if _validation_status is not None and _validation_status is not UNSET:
                try:
                    validation_status = AssayRunValidationStatus(_validation_status)
                except ValueError:
                    validation_status = AssayRunValidationStatus.of_unknown(_validation_status)

            return validation_status

        validation_status = (
            get_validation_status()
            if "validationStatus" in d
            else cast(Union[Unset, AssayRunValidationStatus], UNSET)
        )

        assay_run_create = cls(
            fields=fields,
            schema_id=schema_id,
            id=id,
            project_id=project_id,
            validation_comment=validation_comment,
            validation_status=validation_status,
        )

        assay_run_create.additional_properties = d
        return assay_run_create

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
        """ Object of assay run fields """
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Union[Fields, AssayFieldsCreate, UnknownType]) -> None:
        self._fields = value

    @property
    def schema_id(self) -> str:
        """ ID of assay schema that assay run conforms to """
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @property
    def id(self) -> str:
        """ ID of assay run """
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
    def project_id(self) -> str:
        """The project that the assay run should be uploaded to. Only users with read access to the project will be able to read the assay run. Leaving this empty will result in only the creator having read access."""
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
    def validation_comment(self) -> str:
        """ Additional information about the validation status """
        if isinstance(self._validation_comment, Unset):
            raise NotPresentError(self, "validation_comment")
        return self._validation_comment

    @validation_comment.setter
    def validation_comment(self, value: str) -> None:
        self._validation_comment = value

    @validation_comment.deleter
    def validation_comment(self) -> None:
        self._validation_comment = UNSET

    @property
    def validation_status(self) -> AssayRunValidationStatus:
        """ Must be either VALID or INVALID """
        if isinstance(self._validation_status, Unset):
            raise NotPresentError(self, "validation_status")
        return self._validation_status

    @validation_status.setter
    def validation_status(self, value: AssayRunValidationStatus) -> None:
        self._validation_status = value

    @validation_status.deleter
    def validation_status(self) -> None:
        self._validation_status = UNSET
