from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySchemaConstraint")


@attr.s(auto_attribs=True, repr=False)
class EntitySchemaConstraint:
    """  """

    _field_definition_names: Union[Unset, List[str]] = UNSET
    _has_unique_residues: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("field_definition_names={}".format(repr(self._field_definition_names)))
        fields.append("has_unique_residues={}".format(repr(self._has_unique_residues)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntitySchemaConstraint({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        field_definition_names: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._field_definition_names, Unset):
            field_definition_names = self._field_definition_names

        has_unique_residues = self._has_unique_residues

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_definition_names is not UNSET:
            field_dict["fieldDefinitionNames"] = field_definition_names
        if has_unique_residues is not UNSET:
            field_dict["hasUniqueResidues"] = has_unique_residues

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_field_definition_names() -> Union[Unset, List[str]]:
            field_definition_names = cast(List[str], d.pop("fieldDefinitionNames"))

            return field_definition_names

        field_definition_names = (
            get_field_definition_names()
            if "fieldDefinitionNames" in d
            else cast(Union[Unset, List[str]], UNSET)
        )

        def get_has_unique_residues() -> Union[Unset, bool]:
            has_unique_residues = d.pop("hasUniqueResidues")
            return has_unique_residues

        has_unique_residues = (
            get_has_unique_residues() if "hasUniqueResidues" in d else cast(Union[Unset, bool], UNSET)
        )

        entity_schema_constraint = cls(
            field_definition_names=field_definition_names,
            has_unique_residues=has_unique_residues,
        )

        entity_schema_constraint.additional_properties = d
        return entity_schema_constraint

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
    def field_definition_names(self) -> List[str]:
        if isinstance(self._field_definition_names, Unset):
            raise NotPresentError(self, "field_definition_names")
        return self._field_definition_names

    @field_definition_names.setter
    def field_definition_names(self, value: List[str]) -> None:
        self._field_definition_names = value

    @field_definition_names.deleter
    def field_definition_names(self) -> None:
        self._field_definition_names = UNSET

    @property
    def has_unique_residues(self) -> bool:
        if isinstance(self._has_unique_residues, Unset):
            raise NotPresentError(self, "has_unique_residues")
        return self._has_unique_residues

    @has_unique_residues.setter
    def has_unique_residues(self, value: bool) -> None:
        self._has_unique_residues = value

    @has_unique_residues.deleter
    def has_unique_residues(self) -> None:
        self._has_unique_residues = UNSET
