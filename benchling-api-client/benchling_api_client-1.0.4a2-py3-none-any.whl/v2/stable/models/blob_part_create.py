from typing import Any, cast, Dict, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BlobPartCreate")


@attr.s(auto_attribs=True, repr=False)
class BlobPartCreate:
    """  """

    _data64: str
    _md5: str
    _part_number: int

    def __repr__(self):
        fields = []
        fields.append("data64={}".format(repr(self._data64)))
        fields.append("md5={}".format(repr(self._md5)))
        fields.append("part_number={}".format(repr(self._part_number)))
        return "BlobPartCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        data64 = self._data64
        md5 = self._md5
        part_number = self._part_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data64": data64,
                "md5": md5,
                "partNumber": part_number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_data64() -> str:
            data64 = d.pop("data64")
            return data64

        data64 = get_data64() if "data64" in d else cast(str, UNSET)

        def get_md5() -> str:
            md5 = d.pop("md5")
            return md5

        md5 = get_md5() if "md5" in d else cast(str, UNSET)

        def get_part_number() -> int:
            part_number = d.pop("partNumber")
            return part_number

        part_number = get_part_number() if "partNumber" in d else cast(int, UNSET)

        blob_part_create = cls(
            data64=data64,
            md5=md5,
            part_number=part_number,
        )

        return blob_part_create

    @property
    def data64(self) -> str:
        if isinstance(self._data64, Unset):
            raise NotPresentError(self, "data64")
        return self._data64

    @data64.setter
    def data64(self, value: str) -> None:
        self._data64 = value

    @property
    def md5(self) -> str:
        if isinstance(self._md5, Unset):
            raise NotPresentError(self, "md5")
        return self._md5

    @md5.setter
    def md5(self, value: str) -> None:
        self._md5 = value

    @property
    def part_number(self) -> int:
        """An integer between 1 to 10,000, inclusive. The part number must be unique per part and indicates the ordering of the part inside the final blob. The part numbers do not need to be consecutive."""
        if isinstance(self._part_number, Unset):
            raise NotPresentError(self, "part_number")
        return self._part_number

    @part_number.setter
    def part_number(self, value: int) -> None:
        self._part_number = value
