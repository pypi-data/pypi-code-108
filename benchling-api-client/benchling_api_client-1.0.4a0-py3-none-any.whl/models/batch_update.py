from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.default_concentration_summary import DefaultConcentrationSummary
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchUpdate")


@attr.s(auto_attribs=True, repr=False)
class BatchUpdate:
    """  """

    _default_concentration: Union[Unset, DefaultConcentrationSummary] = UNSET
    _fields: Union[Unset, Fields] = UNSET

    def __repr__(self):
        fields = []
        fields.append("default_concentration={}".format(repr(self._default_concentration)))
        fields.append("fields={}".format(repr(self._fields)))
        return "BatchUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        default_concentration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._default_concentration, Unset):
            default_concentration = self._default_concentration.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if default_concentration is not UNSET:
            field_dict["defaultConcentration"] = default_concentration
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

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        batch_update = cls(
            default_concentration=default_concentration,
            fields=fields,
        )

        return batch_update

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
