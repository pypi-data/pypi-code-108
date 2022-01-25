from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_sequence_summary_entity_type import AaSequenceSummaryEntityType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaSequenceSummary")


@attr.s(auto_attribs=True, repr=False)
class AaSequenceSummary:
    """  """

    _entity_type: Union[Unset, AaSequenceSummaryEntityType] = UNSET
    _id: Union[Unset, str] = UNSET
    _type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_type={}".format(repr(self._entity_type)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AaSequenceSummary({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_type: Union[Unset, int] = UNSET
        if not isinstance(self._entity_type, Unset):
            entity_type = self._entity_type.value

        id = self._id
        type = self._type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entity_type is not UNSET:
            field_dict["entityType"] = entity_type
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_type() -> Union[Unset, AaSequenceSummaryEntityType]:
            entity_type = None
            _entity_type = d.pop("entityType")
            if _entity_type is not None and _entity_type is not UNSET:
                try:
                    entity_type = AaSequenceSummaryEntityType(_entity_type)
                except ValueError:
                    entity_type = AaSequenceSummaryEntityType.of_unknown(_entity_type)

            return entity_type

        entity_type = (
            get_entity_type() if "entityType" in d else cast(Union[Unset, AaSequenceSummaryEntityType], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, str]:
            type = d.pop("type")
            return type

        type = get_type() if "type" in d else cast(Union[Unset, str], UNSET)

        aa_sequence_summary = cls(
            entity_type=entity_type,
            id=id,
            type=type,
        )

        aa_sequence_summary.additional_properties = d
        return aa_sequence_summary

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
    def entity_type(self) -> AaSequenceSummaryEntityType:
        if isinstance(self._entity_type, Unset):
            raise NotPresentError(self, "entity_type")
        return self._entity_type

    @entity_type.setter
    def entity_type(self, value: AaSequenceSummaryEntityType) -> None:
        self._entity_type = value

    @entity_type.deleter
    def entity_type(self) -> None:
        self._entity_type = UNSET

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
    def type(self) -> str:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
