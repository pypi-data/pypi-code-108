from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.blob_part import BlobPart
from ..types import UNSET, Unset

T = TypeVar("T", bound="BlobComplete")


@attr.s(auto_attribs=True, repr=False)
class BlobComplete:
    """  """

    _parts: Union[Unset, List[BlobPart]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("parts={}".format(repr(self._parts)))
        return "BlobComplete({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        parts: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._parts, Unset):
            parts = []
            for parts_item_data in self._parts:
                parts_item = parts_item_data.to_dict()

                parts.append(parts_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if parts is not UNSET:
            field_dict["parts"] = parts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_parts() -> Union[Unset, List[BlobPart]]:
            parts = []
            _parts = d.pop("parts")
            for parts_item_data in _parts or []:
                parts_item = BlobPart.from_dict(parts_item_data)

                parts.append(parts_item)

            return parts

        parts = get_parts() if "parts" in d else cast(Union[Unset, List[BlobPart]], UNSET)

        blob_complete = cls(
            parts=parts,
        )

        return blob_complete

    @property
    def parts(self) -> List[BlobPart]:
        if isinstance(self._parts, Unset):
            raise NotPresentError(self, "parts")
        return self._parts

    @parts.setter
    def parts(self, value: List[BlobPart]) -> None:
        self._parts = value

    @parts.deleter
    def parts(self) -> None:
        self._parts = UNSET
