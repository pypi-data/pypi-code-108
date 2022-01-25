from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="MixturesArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class MixturesArchivalChange:
    """IDs of all mixtures that were archived or unarchived."""

    _mixture_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("mixture_ids={}".format(repr(self._mixture_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "MixturesArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixture_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._mixture_ids, Unset):
            mixture_ids = self._mixture_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mixture_ids is not UNSET:
            field_dict["mixtureIds"] = mixture_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_mixture_ids() -> Union[Unset, List[str]]:
            mixture_ids = cast(List[str], d.pop("mixtureIds"))

            return mixture_ids

        mixture_ids = get_mixture_ids() if "mixtureIds" in d else cast(Union[Unset, List[str]], UNSET)

        mixtures_archival_change = cls(
            mixture_ids=mixture_ids,
        )

        mixtures_archival_change.additional_properties = d
        return mixtures_archival_change

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
    def mixture_ids(self) -> List[str]:
        if isinstance(self._mixture_ids, Unset):
            raise NotPresentError(self, "mixture_ids")
        return self._mixture_ids

    @mixture_ids.setter
    def mixture_ids(self, value: List[str]) -> None:
        self._mixture_ids = value

    @mixture_ids.deleter
    def mixture_ids(self) -> None:
        self._mixture_ids = UNSET
