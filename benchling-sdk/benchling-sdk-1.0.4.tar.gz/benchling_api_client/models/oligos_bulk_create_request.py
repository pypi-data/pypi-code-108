from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.oligo_create import OligoCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="OligosBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class OligosBulkCreateRequest:
    """  """

    _oligos: Union[Unset, List[OligoCreate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("oligos={}".format(repr(self._oligos)))
        return "OligosBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._oligos, Unset):
            oligos = []
            for oligos_item_data in self._oligos:
                oligos_item = oligos_item_data.to_dict()

                oligos.append(oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if oligos is not UNSET:
            field_dict["oligos"] = oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_oligos() -> Union[Unset, List[OligoCreate]]:
            oligos = []
            _oligos = d.pop("oligos")
            for oligos_item_data in _oligos or []:
                oligos_item = OligoCreate.from_dict(oligos_item_data)

                oligos.append(oligos_item)

            return oligos

        oligos = get_oligos() if "oligos" in d else cast(Union[Unset, List[OligoCreate]], UNSET)

        oligos_bulk_create_request = cls(
            oligos=oligos,
        )

        return oligos_bulk_create_request

    @property
    def oligos(self) -> List[OligoCreate]:
        if isinstance(self._oligos, Unset):
            raise NotPresentError(self, "oligos")
        return self._oligos

    @oligos.setter
    def oligos(self, value: List[OligoCreate]) -> None:
        self._oligos = value

    @oligos.deleter
    def oligos(self) -> None:
        self._oligos = UNSET
