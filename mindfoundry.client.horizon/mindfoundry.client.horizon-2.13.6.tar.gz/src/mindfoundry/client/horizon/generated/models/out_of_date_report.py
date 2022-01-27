from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="OutOfDateReport")


@attr.s(auto_attribs=True)
class OutOfDateReport:
    """  """

    out_of_date: bool
    actual_data_split: Union[Unset, float] = UNSET
    intended_data_split: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        out_of_date = self.out_of_date
        actual_data_split = self.actual_data_split
        intended_data_split = self.intended_data_split

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "outOfDate": out_of_date,
            }
        )
        if actual_data_split is not UNSET:
            field_dict["actualDataSplit"] = actual_data_split
        if intended_data_split is not UNSET:
            field_dict["intendedDataSplit"] = intended_data_split

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        out_of_date = d.pop("outOfDate")

        actual_data_split = d.pop("actualDataSplit", UNSET)

        intended_data_split = d.pop("intendedDataSplit", UNSET)

        out_of_date_report = cls(
            out_of_date=out_of_date,
            actual_data_split=actual_data_split,
            intended_data_split=intended_data_split,
        )

        out_of_date_report.additional_properties = d
        return out_of_date_report

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
