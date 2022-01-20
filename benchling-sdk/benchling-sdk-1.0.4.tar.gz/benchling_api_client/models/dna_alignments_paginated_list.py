from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_alignment_summary import DnaAlignmentSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaAlignmentsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class DnaAlignmentsPaginatedList:
    """  """

    _dna_alignments: Union[Unset, List[DnaAlignmentSummary]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dna_alignments={}".format(repr(self._dna_alignments)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaAlignmentsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_alignments: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_alignments, Unset):
            dna_alignments = []
            for dna_alignments_item_data in self._dna_alignments:
                dna_alignments_item = dna_alignments_item_data.to_dict()

                dna_alignments.append(dna_alignments_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dna_alignments is not UNSET:
            field_dict["dnaAlignments"] = dna_alignments
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_alignments() -> Union[Unset, List[DnaAlignmentSummary]]:
            dna_alignments = []
            _dna_alignments = d.pop("dnaAlignments")
            for dna_alignments_item_data in _dna_alignments or []:
                dna_alignments_item = DnaAlignmentSummary.from_dict(dna_alignments_item_data)

                dna_alignments.append(dna_alignments_item)

            return dna_alignments

        dna_alignments = (
            get_dna_alignments()
            if "dnaAlignments" in d
            else cast(Union[Unset, List[DnaAlignmentSummary]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        dna_alignments_paginated_list = cls(
            dna_alignments=dna_alignments,
            next_token=next_token,
        )

        dna_alignments_paginated_list.additional_properties = d
        return dna_alignments_paginated_list

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
    def dna_alignments(self) -> List[DnaAlignmentSummary]:
        if isinstance(self._dna_alignments, Unset):
            raise NotPresentError(self, "dna_alignments")
        return self._dna_alignments

    @dna_alignments.setter
    def dna_alignments(self, value: List[DnaAlignmentSummary]) -> None:
        self._dna_alignments = value

    @dna_alignments.deleter
    def dna_alignments(self) -> None:
        self._dna_alignments = UNSET

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
