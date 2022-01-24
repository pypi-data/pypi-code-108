from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Time")


@attr.s(auto_attribs=True)
class Time:
    """ """

    time: str
    calendarmodel: Union[Unset, str] = UNSET
    timezone: Union[Unset, int] = UNSET
    before: Union[Unset, int] = UNSET
    after: Union[Unset, int] = UNSET
    precision: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        time = self.time
        calendarmodel = self.calendarmodel
        timezone = self.timezone
        before = self.before
        after = self.after
        precision = self.precision

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "time": time,
            }
        )
        if calendarmodel is not UNSET:
            field_dict["calendarmodel"] = calendarmodel
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if before is not UNSET:
            field_dict["before"] = before
        if after is not UNSET:
            field_dict["after"] = after
        if precision is not UNSET:
            field_dict["precision"] = precision

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        time = d.pop("time")

        calendarmodel = d.pop("calendarmodel", UNSET)

        timezone = d.pop("timezone", UNSET)

        before = d.pop("before", UNSET)

        after = d.pop("after", UNSET)

        precision = d.pop("precision", UNSET)

        time = cls(
            time=time,
            calendarmodel=calendarmodel,
            timezone=timezone,
            before=before,
            after=after,
            precision=precision,
        )

        return time
