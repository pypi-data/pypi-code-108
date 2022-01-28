from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.event import Event
from ..types import UNSET, Unset

T = TypeVar("T", bound="EventsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class EventsPaginatedList:
    """  """

    _events: Union[Unset, List[Event]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("events={}".format(repr(self._events)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EventsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        events: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._events, Unset):
            events = []
            for events_item_data in self._events:
                events_item = events_item_data.to_dict()

                events.append(events_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if events is not UNSET:
            field_dict["events"] = events
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_events() -> Union[Unset, List[Event]]:
            events = []
            _events = d.pop("events")
            for events_item_data in _events or []:
                events_item = Event.from_dict(events_item_data)

                events.append(events_item)

            return events

        events = get_events() if "events" in d else cast(Union[Unset, List[Event]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        events_paginated_list = cls(
            events=events,
            next_token=next_token,
        )

        events_paginated_list.additional_properties = d
        return events_paginated_list

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
    def events(self) -> List[Event]:
        if isinstance(self._events, Unset):
            raise NotPresentError(self, "events")
        return self._events

    @events.setter
    def events(self, value: List[Event]) -> None:
        self._events = value

    @events.deleter
    def events(self) -> None:
        self._events = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
