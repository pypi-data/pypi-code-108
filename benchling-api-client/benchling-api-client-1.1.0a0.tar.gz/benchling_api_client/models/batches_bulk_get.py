from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.batch import Batch
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchesBulkGet")


@attr.s(auto_attribs=True, repr=False)
class BatchesBulkGet:
    """  """

    _batches: Union[Unset, List[Batch]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batches={}".format(repr(self._batches)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BatchesBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batches: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._batches, Unset):
            batches = []
            for batches_item_data in self._batches:
                batches_item = batches_item_data.to_dict()

                batches.append(batches_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batches is not UNSET:
            field_dict["batches"] = batches

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_batches() -> Union[Unset, List[Batch]]:
            batches = []
            _batches = d.pop("batches")
            for batches_item_data in _batches or []:
                batches_item = Batch.from_dict(batches_item_data)

                batches.append(batches_item)

            return batches

        batches = get_batches() if "batches" in d else cast(Union[Unset, List[Batch]], UNSET)

        batches_bulk_get = cls(
            batches=batches,
        )

        batches_bulk_get.additional_properties = d
        return batches_bulk_get

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
    def batches(self) -> List[Batch]:
        if isinstance(self._batches, Unset):
            raise NotPresentError(self, "batches")
        return self._batches

    @batches.setter
    def batches(self, value: List[Batch]) -> None:
        self._batches = value

    @batches.deleter
    def batches(self) -> None:
        self._batches = UNSET
