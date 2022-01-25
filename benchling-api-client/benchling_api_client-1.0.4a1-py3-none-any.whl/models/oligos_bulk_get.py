from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.dna_oligo import DnaOligo
from ..models.rna_oligo import RnaOligo
from ..types import UNSET, Unset

T = TypeVar("T", bound="OligosBulkGet")


@attr.s(auto_attribs=True, repr=False)
class OligosBulkGet:
    """  """

    _oligos: Union[Unset, List[Union[DnaOligo, RnaOligo, UnknownType]]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("oligos={}".format(repr(self._oligos)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "OligosBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._oligos, Unset):
            oligos = []
            for oligos_item_data in self._oligos:
                if isinstance(oligos_item_data, UnknownType):
                    oligos_item = oligos_item_data.value
                elif isinstance(oligos_item_data, DnaOligo):
                    oligos_item = oligos_item_data.to_dict()

                else:
                    oligos_item = oligos_item_data.to_dict()

                oligos.append(oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if oligos is not UNSET:
            field_dict["oligos"] = oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_oligos() -> Union[Unset, List[Union[DnaOligo, RnaOligo, UnknownType]]]:
            oligos = []
            _oligos = d.pop("oligos")
            for oligos_item_data in _oligos or []:

                def _parse_oligos_item(data: Union[Dict[str, Any]]) -> Union[DnaOligo, RnaOligo, UnknownType]:
                    oligos_item: Union[DnaOligo, RnaOligo, UnknownType]
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        oligos_item = DnaOligo.from_dict(data)

                        return oligos_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        oligos_item = RnaOligo.from_dict(data)

                        return oligos_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                oligos_item = _parse_oligos_item(oligos_item_data)

                oligos.append(oligos_item)

            return oligos

        oligos = (
            get_oligos()
            if "oligos" in d
            else cast(Union[Unset, List[Union[DnaOligo, RnaOligo, UnknownType]]], UNSET)
        )

        oligos_bulk_get = cls(
            oligos=oligos,
        )

        oligos_bulk_get.additional_properties = d
        return oligos_bulk_get

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
    def oligos(self) -> List[Union[DnaOligo, RnaOligo, UnknownType]]:
        if isinstance(self._oligos, Unset):
            raise NotPresentError(self, "oligos")
        return self._oligos

    @oligos.setter
    def oligos(self, value: List[Union[DnaOligo, RnaOligo, UnknownType]]) -> None:
        self._oligos = value

    @oligos.deleter
    def oligos(self) -> None:
        self._oligos = UNSET
