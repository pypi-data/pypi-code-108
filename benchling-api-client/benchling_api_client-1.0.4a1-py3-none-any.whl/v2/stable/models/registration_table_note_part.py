from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.registration_table_note_part_type import RegistrationTableNotePartType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistrationTableNotePart")


@attr.s(auto_attribs=True, repr=False)
class RegistrationTableNotePart:
    """  """

    _entity_schema_id: Union[Unset, str] = UNSET
    _type: Union[Unset, RegistrationTableNotePartType] = UNSET
    _indentation: Union[Unset, int] = 0
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_schema_id={}".format(repr(self._entity_schema_id)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("indentation={}".format(repr(self._indentation)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RegistrationTableNotePart({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_schema_id = self._entity_schema_id
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        indentation = self._indentation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entity_schema_id is not UNSET:
            field_dict["entitySchemaId"] = entity_schema_id
        if type is not UNSET:
            field_dict["type"] = type
        if indentation is not UNSET:
            field_dict["indentation"] = indentation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_schema_id() -> Union[Unset, str]:
            entity_schema_id = d.pop("entitySchemaId")
            return entity_schema_id

        entity_schema_id = get_entity_schema_id() if "entitySchemaId" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, RegistrationTableNotePartType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = RegistrationTableNotePartType(_type)
                except ValueError:
                    type = RegistrationTableNotePartType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, RegistrationTableNotePartType], UNSET)

        def get_indentation() -> Union[Unset, int]:
            indentation = d.pop("indentation")
            return indentation

        indentation = get_indentation() if "indentation" in d else cast(Union[Unset, int], UNSET)

        registration_table_note_part = cls(
            entity_schema_id=entity_schema_id,
            type=type,
            indentation=indentation,
        )

        registration_table_note_part.additional_properties = d
        return registration_table_note_part

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
    def entity_schema_id(self) -> str:
        if isinstance(self._entity_schema_id, Unset):
            raise NotPresentError(self, "entity_schema_id")
        return self._entity_schema_id

    @entity_schema_id.setter
    def entity_schema_id(self, value: str) -> None:
        self._entity_schema_id = value

    @entity_schema_id.deleter
    def entity_schema_id(self) -> None:
        self._entity_schema_id = UNSET

    @property
    def type(self) -> RegistrationTableNotePartType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: RegistrationTableNotePartType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def indentation(self) -> int:
        """All notes have an indentation level - the default is 0 for no indent. For lists, indentation gives notes hierarchy - a bulleted list with children is modeled as one note part with indentation 1 followed by note parts with indentation 2, for example."""
        if isinstance(self._indentation, Unset):
            raise NotPresentError(self, "indentation")
        return self._indentation

    @indentation.setter
    def indentation(self, value: int) -> None:
        self._indentation = value

    @indentation.deleter
    def indentation(self) -> None:
        self._indentation = UNSET
