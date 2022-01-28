from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.molecule_bulk_update import MoleculeBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="MoleculesBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class MoleculesBulkUpdateRequest:
    """  """

    _molecules: Union[Unset, List[MoleculeBulkUpdate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("molecules={}".format(repr(self._molecules)))
        return "MoleculesBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        molecules: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._molecules, Unset):
            molecules = []
            for molecules_item_data in self._molecules:
                molecules_item = molecules_item_data.to_dict()

                molecules.append(molecules_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if molecules is not UNSET:
            field_dict["molecules"] = molecules

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_molecules() -> Union[Unset, List[MoleculeBulkUpdate]]:
            molecules = []
            _molecules = d.pop("molecules")
            for molecules_item_data in _molecules or []:
                molecules_item = MoleculeBulkUpdate.from_dict(molecules_item_data)

                molecules.append(molecules_item)

            return molecules

        molecules = (
            get_molecules() if "molecules" in d else cast(Union[Unset, List[MoleculeBulkUpdate]], UNSET)
        )

        molecules_bulk_update_request = cls(
            molecules=molecules,
        )

        return molecules_bulk_update_request

    @property
    def molecules(self) -> List[MoleculeBulkUpdate]:
        if isinstance(self._molecules, Unset):
            raise NotPresentError(self, "molecules")
        return self._molecules

    @molecules.setter
    def molecules(self, value: List[MoleculeBulkUpdate]) -> None:
        self._molecules = value

    @molecules.deleter
    def molecules(self) -> None:
        self._molecules = UNSET
