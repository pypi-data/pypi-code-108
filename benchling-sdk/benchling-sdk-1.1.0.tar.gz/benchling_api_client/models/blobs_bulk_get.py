from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.blob import Blob
from ..types import UNSET, Unset

T = TypeVar("T", bound="BlobsBulkGet")


@attr.s(auto_attribs=True, repr=False)
class BlobsBulkGet:
    """  """

    _blobs: Union[Unset, List[Blob]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("blobs={}".format(repr(self._blobs)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BlobsBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        blobs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._blobs, Unset):
            blobs = []
            for blobs_item_data in self._blobs:
                blobs_item = blobs_item_data.to_dict()

                blobs.append(blobs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if blobs is not UNSET:
            field_dict["blobs"] = blobs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_blobs() -> Union[Unset, List[Blob]]:
            blobs = []
            _blobs = d.pop("blobs")
            for blobs_item_data in _blobs or []:
                blobs_item = Blob.from_dict(blobs_item_data)

                blobs.append(blobs_item)

            return blobs

        blobs = get_blobs() if "blobs" in d else cast(Union[Unset, List[Blob]], UNSET)

        blobs_bulk_get = cls(
            blobs=blobs,
        )

        blobs_bulk_get.additional_properties = d
        return blobs_bulk_get

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
    def blobs(self) -> List[Blob]:
        if isinstance(self._blobs, Unset):
            raise NotPresentError(self, "blobs")
        return self._blobs

    @blobs.setter
    def blobs(self, value: List[Blob]) -> None:
        self._blobs = value

    @blobs.deleter
    def blobs(self) -> None:
        self._blobs = UNSET
