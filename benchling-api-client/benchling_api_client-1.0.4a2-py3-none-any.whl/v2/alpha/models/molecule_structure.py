from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.molecule_structure_structure_format import MoleculeStructureStructureFormat
from ..types import UNSET, Unset

T = TypeVar("T", bound="MoleculeStructure")


@attr.s(auto_attribs=True, repr=False)
class MoleculeStructure:
    """  """

    _structure_format: Union[Unset, MoleculeStructureStructureFormat] = UNSET
    _value: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("structure_format={}".format(repr(self._structure_format)))
        fields.append("value={}".format(repr(self._value)))
        return "MoleculeStructure({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        structure_format: Union[Unset, int] = UNSET
        if not isinstance(self._structure_format, Unset):
            structure_format = self._structure_format.value

        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if structure_format is not UNSET:
            field_dict["structureFormat"] = structure_format
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_structure_format() -> Union[Unset, MoleculeStructureStructureFormat]:
            structure_format = None
            _structure_format = d.pop("structureFormat")
            if _structure_format is not None and _structure_format is not UNSET:
                try:
                    structure_format = MoleculeStructureStructureFormat(_structure_format)
                except ValueError:
                    structure_format = MoleculeStructureStructureFormat.of_unknown(_structure_format)

            return structure_format

        structure_format = (
            get_structure_format()
            if "structureFormat" in d
            else cast(Union[Unset, MoleculeStructureStructureFormat], UNSET)
        )

        def get_value() -> Union[Unset, str]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Union[Unset, str], UNSET)

        molecule_structure = cls(
            structure_format=structure_format,
            value=value,
        )

        return molecule_structure

    @property
    def structure_format(self) -> MoleculeStructureStructureFormat:
        if isinstance(self._structure_format, Unset):
            raise NotPresentError(self, "structure_format")
        return self._structure_format

    @structure_format.setter
    def structure_format(self, value: MoleculeStructureStructureFormat) -> None:
        self._structure_format = value

    @structure_format.deleter
    def structure_format(self) -> None:
        self._structure_format = UNSET

    @property
    def value(self) -> str:
        """ Molecular structure in SMILES or molfile format. """
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @value.deleter
    def value(self) -> None:
        self._value = UNSET
