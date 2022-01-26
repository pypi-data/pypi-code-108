from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CoreDate")


@define(auto_attribs=True)
class CoreDate:
    """
    Attributes:
        day (Union[Unset, int]): Day of a month. Must be from 1 to 31 and valid for the year and month, or 0 to specify
            a year by itself or a year and month where the day isn't significant.Month of a year. Must be from 1 to 12, or 0
            to specify a year without a month and day. Example: 16.
        month (Union[Unset, int]): Month of a year. Must be from 1 to 12, or 0 to specify a year without a month and
            day. Example: 1.
        year (Union[Unset, int]): Year of the date. Must be from 1 to 9999, or 0 to specify a date without a year
            Example: 2020.
    """

    day: Union[Unset, int] = UNSET
    month: Union[Unset, int] = UNSET
    year: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        day = self.day
        month = self.month
        year = self.year

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if day is not UNSET:
            field_dict["day"] = day
        if month is not UNSET:
            field_dict["month"] = month
        if year is not UNSET:
            field_dict["year"] = year

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        day = d.pop("day", UNSET)

        month = d.pop("month", UNSET)

        year = d.pop("year", UNSET)

        core_date = cls(
            day=day,
            month=month,
            year=year,
        )

        core_date.additional_properties = d
        return core_date

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
