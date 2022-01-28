import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistrationOrigin")


@attr.s(auto_attribs=True, repr=False)
class RegistrationOrigin:
    """  """

    _origin_entry_id: Union[Unset, None, str] = UNSET
    _registered_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("origin_entry_id={}".format(repr(self._origin_entry_id)))
        fields.append("registered_at={}".format(repr(self._registered_at)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RegistrationOrigin({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        origin_entry_id = self._origin_entry_id
        registered_at: Union[Unset, str] = UNSET
        if not isinstance(self._registered_at, Unset):
            registered_at = self._registered_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if origin_entry_id is not UNSET:
            field_dict["originEntryId"] = origin_entry_id
        if registered_at is not UNSET:
            field_dict["registeredAt"] = registered_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_origin_entry_id() -> Union[Unset, None, str]:
            origin_entry_id = d.pop("originEntryId")
            return origin_entry_id

        origin_entry_id = (
            get_origin_entry_id() if "originEntryId" in d else cast(Union[Unset, None, str], UNSET)
        )

        def get_registered_at() -> Union[Unset, datetime.datetime]:
            registered_at: Union[Unset, datetime.datetime] = UNSET
            _registered_at = d.pop("registeredAt")
            if _registered_at is not None and not isinstance(_registered_at, Unset):
                registered_at = isoparse(cast(str, _registered_at))

            return registered_at

        registered_at = (
            get_registered_at() if "registeredAt" in d else cast(Union[Unset, datetime.datetime], UNSET)
        )

        registration_origin = cls(
            origin_entry_id=origin_entry_id,
            registered_at=registered_at,
        )

        registration_origin.additional_properties = d
        return registration_origin

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
    def origin_entry_id(self) -> Optional[str]:
        if isinstance(self._origin_entry_id, Unset):
            raise NotPresentError(self, "origin_entry_id")
        return self._origin_entry_id

    @origin_entry_id.setter
    def origin_entry_id(self, value: Optional[str]) -> None:
        self._origin_entry_id = value

    @origin_entry_id.deleter
    def origin_entry_id(self) -> None:
        self._origin_entry_id = UNSET

    @property
    def registered_at(self) -> datetime.datetime:
        if isinstance(self._registered_at, Unset):
            raise NotPresentError(self, "registered_at")
        return self._registered_at

    @registered_at.setter
    def registered_at(self, value: datetime.datetime) -> None:
        self._registered_at = value

    @registered_at.deleter
    def registered_at(self) -> None:
        self._registered_at = UNSET
