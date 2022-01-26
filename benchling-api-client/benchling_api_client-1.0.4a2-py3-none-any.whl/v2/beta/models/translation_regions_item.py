from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="TranslationRegionsItem")


@attr.s(auto_attribs=True, repr=False)
class TranslationRegionsItem:
    """  """

    _end: Union[Unset, int] = UNSET
    _start: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("end={}".format(repr(self._end)))
        fields.append("start={}".format(repr(self._start)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TranslationRegionsItem({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        end = self._end
        start = self._start

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if end is not UNSET:
            field_dict["end"] = end
        if start is not UNSET:
            field_dict["start"] = start

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_end() -> Union[Unset, int]:
            end = d.pop("end")
            return end

        end = get_end() if "end" in d else cast(Union[Unset, int], UNSET)

        def get_start() -> Union[Unset, int]:
            start = d.pop("start")
            return start

        start = get_start() if "start" in d else cast(Union[Unset, int], UNSET)

        translation_regions_item = cls(
            end=end,
            start=start,
        )

        translation_regions_item.additional_properties = d
        return translation_regions_item

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
    def end(self) -> int:
        if isinstance(self._end, Unset):
            raise NotPresentError(self, "end")
        return self._end

    @end.setter
    def end(self, value: int) -> None:
        self._end = value

    @end.deleter
    def end(self) -> None:
        self._end = UNSET

    @property
    def start(self) -> int:
        if isinstance(self._start, Unset):
            raise NotPresentError(self, "start")
        return self._start

    @start.setter
    def start(self, value: int) -> None:
        self._start = value

    @start.deleter
    def start(self) -> None:
        self._start = UNSET
