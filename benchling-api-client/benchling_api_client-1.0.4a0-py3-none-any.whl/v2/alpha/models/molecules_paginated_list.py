from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.molecule import Molecule
from ..types import UNSET, Unset

T = TypeVar("T", bound="MoleculesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class MoleculesPaginatedList:
    """  """

    _molecules: Union[Unset, List[Molecule]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("molecules={}".format(repr(self._molecules)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "MoleculesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        molecules: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._molecules, Unset):
            molecules = []
            for molecules_item_data in self._molecules:
                molecules_item = molecules_item_data.to_dict()

                molecules.append(molecules_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if molecules is not UNSET:
            field_dict["molecules"] = molecules
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_molecules() -> Union[Unset, List[Molecule]]:
            molecules = []
            _molecules = d.pop("molecules")
            for molecules_item_data in _molecules or []:
                molecules_item = Molecule.from_dict(molecules_item_data)

                molecules.append(molecules_item)

            return molecules

        molecules = get_molecules() if "molecules" in d else cast(Union[Unset, List[Molecule]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        molecules_paginated_list = cls(
            molecules=molecules,
            next_token=next_token,
        )

        return molecules_paginated_list

    @property
    def molecules(self) -> List[Molecule]:
        if isinstance(self._molecules, Unset):
            raise NotPresentError(self, "molecules")
        return self._molecules

    @molecules.setter
    def molecules(self, value: List[Molecule]) -> None:
        self._molecules = value

    @molecules.deleter
    def molecules(self) -> None:
        self._molecules = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
