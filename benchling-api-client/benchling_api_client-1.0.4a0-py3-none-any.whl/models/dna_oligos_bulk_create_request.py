from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_oligo_create import DnaOligoCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaOligosBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosBulkCreateRequest:
    """  """

    _dna_oligos: Union[Unset, List[DnaOligoCreate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        return "DnaOligosBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_oligos, Unset):
            dna_oligos = []
            for dna_oligos_item_data in self._dna_oligos:
                dna_oligos_item = dna_oligos_item_data.to_dict()

                dna_oligos.append(dna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if dna_oligos is not UNSET:
            field_dict["dnaOligos"] = dna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_oligos() -> Union[Unset, List[DnaOligoCreate]]:
            dna_oligos = []
            _dna_oligos = d.pop("dnaOligos")
            for dna_oligos_item_data in _dna_oligos or []:
                dna_oligos_item = DnaOligoCreate.from_dict(dna_oligos_item_data)

                dna_oligos.append(dna_oligos_item)

            return dna_oligos

        dna_oligos = get_dna_oligos() if "dnaOligos" in d else cast(Union[Unset, List[DnaOligoCreate]], UNSET)

        dna_oligos_bulk_create_request = cls(
            dna_oligos=dna_oligos,
        )

        return dna_oligos_bulk_create_request

    @property
    def dna_oligos(self) -> List[DnaOligoCreate]:
        if isinstance(self._dna_oligos, Unset):
            raise NotPresentError(self, "dna_oligos")
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[DnaOligoCreate]) -> None:
        self._dna_oligos = value

    @dna_oligos.deleter
    def dna_oligos(self) -> None:
        self._dna_oligos = UNSET
