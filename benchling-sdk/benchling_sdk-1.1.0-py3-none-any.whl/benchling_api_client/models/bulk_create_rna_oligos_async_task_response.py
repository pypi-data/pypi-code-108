from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.rna_oligo import RnaOligo
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkCreateRnaOligosAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkCreateRnaOligosAsyncTaskResponse:
    """  """

    _rna_oligos: Union[Unset, List[RnaOligo]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("rna_oligos={}".format(repr(self._rna_oligos)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkCreateRnaOligosAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rna_oligos, Unset):
            rna_oligos = []
            for rna_oligos_item_data in self._rna_oligos:
                rna_oligos_item = rna_oligos_item_data.to_dict()

                rna_oligos.append(rna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rna_oligos is not UNSET:
            field_dict["rnaOligos"] = rna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rna_oligos() -> Union[Unset, List[RnaOligo]]:
            rna_oligos = []
            _rna_oligos = d.pop("rnaOligos")
            for rna_oligos_item_data in _rna_oligos or []:
                rna_oligos_item = RnaOligo.from_dict(rna_oligos_item_data)

                rna_oligos.append(rna_oligos_item)

            return rna_oligos

        rna_oligos = get_rna_oligos() if "rnaOligos" in d else cast(Union[Unset, List[RnaOligo]], UNSET)

        bulk_create_rna_oligos_async_task_response = cls(
            rna_oligos=rna_oligos,
        )

        bulk_create_rna_oligos_async_task_response.additional_properties = d
        return bulk_create_rna_oligos_async_task_response

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
    def rna_oligos(self) -> List[RnaOligo]:
        if isinstance(self._rna_oligos, Unset):
            raise NotPresentError(self, "rna_oligos")
        return self._rna_oligos

    @rna_oligos.setter
    def rna_oligos(self, value: List[RnaOligo]) -> None:
        self._rna_oligos = value

    @rna_oligos.deleter
    def rna_oligos(self) -> None:
        self._rna_oligos = UNSET
