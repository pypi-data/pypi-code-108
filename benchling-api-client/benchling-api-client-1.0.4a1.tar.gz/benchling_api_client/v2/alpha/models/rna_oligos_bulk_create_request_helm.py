from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.oligo_create_helm import OligoCreateHelm
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaOligosBulkCreateRequestHelm")


@attr.s(auto_attribs=True, repr=False)
class RnaOligosBulkCreateRequestHelm:
    """  """

    _rna_oligos: Union[Unset, List[OligoCreateHelm]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("rna_oligos={}".format(repr(self._rna_oligos)))
        return "RnaOligosBulkCreateRequestHelm({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rna_oligos, Unset):
            rna_oligos = []
            for rna_oligos_item_data in self._rna_oligos:
                rna_oligos_item = rna_oligos_item_data.to_dict()

                rna_oligos.append(rna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if rna_oligos is not UNSET:
            field_dict["rnaOligos"] = rna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rna_oligos() -> Union[Unset, List[OligoCreateHelm]]:
            rna_oligos = []
            _rna_oligos = d.pop("rnaOligos")
            for rna_oligos_item_data in _rna_oligos or []:
                rna_oligos_item = OligoCreateHelm.from_dict(rna_oligos_item_data)

                rna_oligos.append(rna_oligos_item)

            return rna_oligos

        rna_oligos = (
            get_rna_oligos() if "rnaOligos" in d else cast(Union[Unset, List[OligoCreateHelm]], UNSET)
        )

        rna_oligos_bulk_create_request_helm = cls(
            rna_oligos=rna_oligos,
        )

        return rna_oligos_bulk_create_request_helm

    @property
    def rna_oligos(self) -> List[OligoCreateHelm]:
        if isinstance(self._rna_oligos, Unset):
            raise NotPresentError(self, "rna_oligos")
        return self._rna_oligos

    @rna_oligos.setter
    def rna_oligos(self, value: List[OligoCreateHelm]) -> None:
        self._rna_oligos = value

    @rna_oligos.deleter
    def rna_oligos(self) -> None:
        self._rna_oligos = UNSET
