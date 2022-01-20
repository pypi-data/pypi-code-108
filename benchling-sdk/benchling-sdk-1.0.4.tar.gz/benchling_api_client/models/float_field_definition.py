from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.float_field_definition_type import FloatFieldDefinitionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="FloatFieldDefinition")


@attr.s(auto_attribs=True, repr=False)
class FloatFieldDefinition:
    """  """

    _decimal_precision: Union[Unset, None, float] = UNSET
    _legal_text_dropdown_id: Union[Unset, None, str] = UNSET
    _numeric_max: Union[Unset, None, float] = UNSET
    _numeric_min: Union[Unset, None, float] = UNSET
    _type: Union[Unset, FloatFieldDefinitionType] = UNSET
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _id: Union[Unset, str] = UNSET
    _is_multi: Union[Unset, bool] = UNSET
    _is_required: Union[Unset, bool] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("decimal_precision={}".format(repr(self._decimal_precision)))
        fields.append("legal_text_dropdown_id={}".format(repr(self._legal_text_dropdown_id)))
        fields.append("numeric_max={}".format(repr(self._numeric_max)))
        fields.append("numeric_min={}".format(repr(self._numeric_min)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("is_multi={}".format(repr(self._is_multi)))
        fields.append("is_required={}".format(repr(self._is_required)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FloatFieldDefinition({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        decimal_precision = self._decimal_precision
        legal_text_dropdown_id = self._legal_text_dropdown_id
        numeric_max = self._numeric_max
        numeric_min = self._numeric_min
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        id = self._id
        is_multi = self._is_multi
        is_required = self._is_required
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if decimal_precision is not UNSET:
            field_dict["decimalPrecision"] = decimal_precision
        if legal_text_dropdown_id is not UNSET:
            field_dict["legalTextDropdownId"] = legal_text_dropdown_id
        if numeric_max is not UNSET:
            field_dict["numericMax"] = numeric_max
        if numeric_min is not UNSET:
            field_dict["numericMin"] = numeric_min
        if type is not UNSET:
            field_dict["type"] = type
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if id is not UNSET:
            field_dict["id"] = id
        if is_multi is not UNSET:
            field_dict["isMulti"] = is_multi
        if is_required is not UNSET:
            field_dict["isRequired"] = is_required
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_decimal_precision() -> Union[Unset, None, float]:
            decimal_precision = d.pop("decimalPrecision")
            return decimal_precision

        decimal_precision = (
            get_decimal_precision() if "decimalPrecision" in d else cast(Union[Unset, None, float], UNSET)
        )

        def get_legal_text_dropdown_id() -> Union[Unset, None, str]:
            legal_text_dropdown_id = d.pop("legalTextDropdownId")
            return legal_text_dropdown_id

        legal_text_dropdown_id = (
            get_legal_text_dropdown_id()
            if "legalTextDropdownId" in d
            else cast(Union[Unset, None, str], UNSET)
        )

        def get_numeric_max() -> Union[Unset, None, float]:
            numeric_max = d.pop("numericMax")
            return numeric_max

        numeric_max = get_numeric_max() if "numericMax" in d else cast(Union[Unset, None, float], UNSET)

        def get_numeric_min() -> Union[Unset, None, float]:
            numeric_min = d.pop("numericMin")
            return numeric_min

        numeric_min = get_numeric_min() if "numericMin" in d else cast(Union[Unset, None, float], UNSET)

        def get_type() -> Union[Unset, FloatFieldDefinitionType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = FloatFieldDefinitionType(_type)
                except ValueError:
                    type = FloatFieldDefinitionType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, FloatFieldDefinitionType], UNSET)

        def get_archive_record() -> Union[Unset, None, ArchiveRecord]:
            archive_record = None
            _archive_record = d.pop("archiveRecord")
            if _archive_record is not None and not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecord.from_dict(_archive_record)

            return archive_record

        archive_record = (
            get_archive_record() if "archiveRecord" in d else cast(Union[Unset, None, ArchiveRecord], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_is_multi() -> Union[Unset, bool]:
            is_multi = d.pop("isMulti")
            return is_multi

        is_multi = get_is_multi() if "isMulti" in d else cast(Union[Unset, bool], UNSET)

        def get_is_required() -> Union[Unset, bool]:
            is_required = d.pop("isRequired")
            return is_required

        is_required = get_is_required() if "isRequired" in d else cast(Union[Unset, bool], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        float_field_definition = cls(
            decimal_precision=decimal_precision,
            legal_text_dropdown_id=legal_text_dropdown_id,
            numeric_max=numeric_max,
            numeric_min=numeric_min,
            type=type,
            archive_record=archive_record,
            id=id,
            is_multi=is_multi,
            is_required=is_required,
            name=name,
        )

        float_field_definition.additional_properties = d
        return float_field_definition

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
    def decimal_precision(self) -> Optional[float]:
        if isinstance(self._decimal_precision, Unset):
            raise NotPresentError(self, "decimal_precision")
        return self._decimal_precision

    @decimal_precision.setter
    def decimal_precision(self, value: Optional[float]) -> None:
        self._decimal_precision = value

    @decimal_precision.deleter
    def decimal_precision(self) -> None:
        self._decimal_precision = UNSET

    @property
    def legal_text_dropdown_id(self) -> Optional[str]:
        if isinstance(self._legal_text_dropdown_id, Unset):
            raise NotPresentError(self, "legal_text_dropdown_id")
        return self._legal_text_dropdown_id

    @legal_text_dropdown_id.setter
    def legal_text_dropdown_id(self, value: Optional[str]) -> None:
        self._legal_text_dropdown_id = value

    @legal_text_dropdown_id.deleter
    def legal_text_dropdown_id(self) -> None:
        self._legal_text_dropdown_id = UNSET

    @property
    def numeric_max(self) -> Optional[float]:
        if isinstance(self._numeric_max, Unset):
            raise NotPresentError(self, "numeric_max")
        return self._numeric_max

    @numeric_max.setter
    def numeric_max(self, value: Optional[float]) -> None:
        self._numeric_max = value

    @numeric_max.deleter
    def numeric_max(self) -> None:
        self._numeric_max = UNSET

    @property
    def numeric_min(self) -> Optional[float]:
        if isinstance(self._numeric_min, Unset):
            raise NotPresentError(self, "numeric_min")
        return self._numeric_min

    @numeric_min.setter
    def numeric_min(self, value: Optional[float]) -> None:
        self._numeric_min = value

    @numeric_min.deleter
    def numeric_min(self) -> None:
        self._numeric_min = UNSET

    @property
    def type(self) -> FloatFieldDefinitionType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: FloatFieldDefinitionType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

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
    def id(self) -> str:
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
    def is_multi(self) -> bool:
        if isinstance(self._is_multi, Unset):
            raise NotPresentError(self, "is_multi")
        return self._is_multi

    @is_multi.setter
    def is_multi(self, value: bool) -> None:
        self._is_multi = value

    @is_multi.deleter
    def is_multi(self) -> None:
        self._is_multi = UNSET

    @property
    def is_required(self) -> bool:
        if isinstance(self._is_required, Unset):
            raise NotPresentError(self, "is_required")
        return self._is_required

    @is_required.setter
    def is_required(self, value: bool) -> None:
        self._is_required = value

    @is_required.deleter
    def is_required(self) -> None:
        self._is_required = UNSET

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
