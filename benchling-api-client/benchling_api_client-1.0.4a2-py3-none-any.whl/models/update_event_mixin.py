from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateEventMixin")


@attr.s(auto_attribs=True, repr=False)
class UpdateEventMixin:
    """  """

    _updates: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("updates={}".format(repr(self._updates)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "UpdateEventMixin({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        updates: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._updates, Unset):
            updates = self._updates

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if updates is not UNSET:
            field_dict["updates"] = updates

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_updates() -> Union[Unset, List[str]]:
            updates = cast(List[str], d.pop("updates"))

            return updates

        updates = get_updates() if "updates" in d else cast(Union[Unset, List[str]], UNSET)

        update_event_mixin = cls(
            updates=updates,
        )

        update_event_mixin.additional_properties = d
        return update_event_mixin

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
    def updates(self) -> List[str]:
        """These properties have been updated, causing this message"""
        if isinstance(self._updates, Unset):
            raise NotPresentError(self, "updates")
        return self._updates

    @updates.setter
    def updates(self, value: List[str]) -> None:
        self._updates = value

    @updates.deleter
    def updates(self) -> None:
        self._updates = UNSET
