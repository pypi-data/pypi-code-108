from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="MoleculesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class MoleculesUnarchive:
    """The request body for unarchiving Molecules."""

    _molecule_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("molecule_ids={}".format(repr(self._molecule_ids)))
        return "MoleculesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        molecule_ids = self._molecule_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "moleculeIds": molecule_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_molecule_ids() -> List[str]:
            molecule_ids = cast(List[str], d.pop("moleculeIds"))

            return molecule_ids

        molecule_ids = get_molecule_ids() if "moleculeIds" in d else cast(List[str], UNSET)

        molecules_unarchive = cls(
            molecule_ids=molecule_ids,
        )

        return molecules_unarchive

    @property
    def molecule_ids(self) -> List[str]:
        if isinstance(self._molecule_ids, Unset):
            raise NotPresentError(self, "molecule_ids")
        return self._molecule_ids

    @molecule_ids.setter
    def molecule_ids(self, value: List[str]) -> None:
        self._molecule_ids = value
