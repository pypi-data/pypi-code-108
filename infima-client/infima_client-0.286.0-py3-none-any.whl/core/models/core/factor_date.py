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

T = TypeVar("T", bound="CoreFactorDate")


@define(auto_attribs=True)
class CoreFactorDate:
    """
    Attributes:
        month (Union[Unset, int]): Factor date year month. Must be from 1 to 12, or 0 to specify a year without a month
            and day. Example: 1.
        year (Union[Unset, int]): Factor date year. Must be from 1 to 9999, or 0 to specify a date without a year
            Example: 2020.
    """

    month: Union[Unset, int] = UNSET
    year: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        month = self.month
        year = self.year

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if month is not UNSET:
            field_dict["month"] = month
        if year is not UNSET:
            field_dict["year"] = year

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        month = d.pop("month", UNSET)

        year = d.pop("year", UNSET)

        core_factor_date = cls(
            month=month,
            year=year,
        )

        core_factor_date.additional_properties = d
        return core_factor_date

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
