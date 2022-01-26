from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_oligo import DnaOligo
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkCreateDnaOligosAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkCreateDnaOligosAsyncTaskResponse:
    """  """

    _dna_oligos: Union[Unset, List[DnaOligo]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkCreateDnaOligosAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_oligos, Unset):
            dna_oligos = []
            for dna_oligos_item_data in self._dna_oligos:
                dna_oligos_item = dna_oligos_item_data.to_dict()

                dna_oligos.append(dna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dna_oligos is not UNSET:
            field_dict["dnaOligos"] = dna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_oligos() -> Union[Unset, List[DnaOligo]]:
            dna_oligos = []
            _dna_oligos = d.pop("dnaOligos")
            for dna_oligos_item_data in _dna_oligos or []:
                dna_oligos_item = DnaOligo.from_dict(dna_oligos_item_data)

                dna_oligos.append(dna_oligos_item)

            return dna_oligos

        dna_oligos = get_dna_oligos() if "dnaOligos" in d else cast(Union[Unset, List[DnaOligo]], UNSET)

        bulk_create_dna_oligos_async_task_response = cls(
            dna_oligos=dna_oligos,
        )

        bulk_create_dna_oligos_async_task_response.additional_properties = d
        return bulk_create_dna_oligos_async_task_response

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
    def dna_oligos(self) -> List[DnaOligo]:
        if isinstance(self._dna_oligos, Unset):
            raise NotPresentError(self, "dna_oligos")
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[DnaOligo]) -> None:
        self._dna_oligos = value

    @dna_oligos.deleter
    def dna_oligos(self) -> None:
        self._dna_oligos = UNSET
