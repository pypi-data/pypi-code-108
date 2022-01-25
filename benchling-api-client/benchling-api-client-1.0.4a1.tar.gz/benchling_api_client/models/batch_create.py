from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.default_concentration_summary import DefaultConcentrationSummary
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchCreate")


@attr.s(auto_attribs=True, repr=False)
class BatchCreate:
    """  """

    _default_concentration: Union[Unset, DefaultConcentrationSummary] = UNSET
    _entity_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET

    def __repr__(self):
        fields = []
        fields.append("default_concentration={}".format(repr(self._default_concentration)))
        fields.append("entity_id={}".format(repr(self._entity_id)))
        fields.append("fields={}".format(repr(self._fields)))
        return "BatchCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        default_concentration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._default_concentration, Unset):
            default_concentration = self._default_concentration.to_dict()

        entity_id = self._entity_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if default_concentration is not UNSET:
            field_dict["defaultConcentration"] = default_concentration
        if entity_id is not UNSET:
            field_dict["entityId"] = entity_id
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_default_concentration() -> Union[Unset, DefaultConcentrationSummary]:
            default_concentration: Union[Unset, DefaultConcentrationSummary] = UNSET
            _default_concentration = d.pop("defaultConcentration")
            if not isinstance(_default_concentration, Unset):
                default_concentration = DefaultConcentrationSummary.from_dict(_default_concentration)

            return default_concentration

        default_concentration = (
            get_default_concentration()
            if "defaultConcentration" in d
            else cast(Union[Unset, DefaultConcentrationSummary], UNSET)
        )

        def get_entity_id() -> Union[Unset, str]:
            entity_id = d.pop("entityId")
            return entity_id

        entity_id = get_entity_id() if "entityId" in d else cast(Union[Unset, str], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        batch_create = cls(
            default_concentration=default_concentration,
            entity_id=entity_id,
            fields=fields,
        )

        return batch_create

    @property
    def default_concentration(self) -> DefaultConcentrationSummary:
        if isinstance(self._default_concentration, Unset):
            raise NotPresentError(self, "default_concentration")
        return self._default_concentration

    @default_concentration.setter
    def default_concentration(self, value: DefaultConcentrationSummary) -> None:
        self._default_concentration = value

    @default_concentration.deleter
    def default_concentration(self) -> None:
        self._default_concentration = UNSET

    @property
    def entity_id(self) -> str:
        """ API identifier for the entity that the batch will be added to. """
        if isinstance(self._entity_id, Unset):
            raise NotPresentError(self, "entity_id")
        return self._entity_id

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        self._entity_id = value

    @entity_id.deleter
    def entity_id(self) -> None:
        self._entity_id = UNSET

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
