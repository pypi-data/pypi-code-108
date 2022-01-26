from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BlobPart")


@attr.s(auto_attribs=True, repr=False)
class BlobPart:
    """  """

    _e_tag: Union[Unset, str] = UNSET
    _part_number: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("e_tag={}".format(repr(self._e_tag)))
        fields.append("part_number={}".format(repr(self._part_number)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BlobPart({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        e_tag = self._e_tag
        part_number = self._part_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if e_tag is not UNSET:
            field_dict["eTag"] = e_tag
        if part_number is not UNSET:
            field_dict["partNumber"] = part_number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_e_tag() -> Union[Unset, str]:
            e_tag = d.pop("eTag")
            return e_tag

        e_tag = get_e_tag() if "eTag" in d else cast(Union[Unset, str], UNSET)

        def get_part_number() -> Union[Unset, int]:
            part_number = d.pop("partNumber")
            return part_number

        part_number = get_part_number() if "partNumber" in d else cast(Union[Unset, int], UNSET)

        blob_part = cls(
            e_tag=e_tag,
            part_number=part_number,
        )

        blob_part.additional_properties = d
        return blob_part

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
    def e_tag(self) -> str:
        if isinstance(self._e_tag, Unset):
            raise NotPresentError(self, "e_tag")
        return self._e_tag

    @e_tag.setter
    def e_tag(self, value: str) -> None:
        self._e_tag = value

    @e_tag.deleter
    def e_tag(self) -> None:
        self._e_tag = UNSET

    @property
    def part_number(self) -> int:
        if isinstance(self._part_number, Unset):
            raise NotPresentError(self, "part_number")
        return self._part_number

    @part_number.setter
    def part_number(self, value: int) -> None:
        self._part_number = value

    @part_number.deleter
    def part_number(self) -> None:
        self._part_number = UNSET
