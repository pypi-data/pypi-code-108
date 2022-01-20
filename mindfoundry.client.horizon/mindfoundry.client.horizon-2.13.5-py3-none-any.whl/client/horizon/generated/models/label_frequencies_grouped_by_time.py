from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="LabelFrequenciesGroupedByTime")


@attr.s(auto_attribs=True)
class LabelFrequenciesGroupedByTime:
    """  """

    dates_milliseconds: Union[Unset, List[int]] = UNSET
    labels: Union[Unset, List[str]] = UNSET
    frequencies_by_date_by_label: Union[Unset, List[List[int]]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dates_milliseconds: Union[Unset, List[int]] = UNSET
        if not isinstance(self.dates_milliseconds, Unset):
            dates_milliseconds = self.dates_milliseconds

        labels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        frequencies_by_date_by_label: Union[Unset, List[List[int]]] = UNSET
        if not isinstance(self.frequencies_by_date_by_label, Unset):
            frequencies_by_date_by_label = []
            for frequencies_by_date_by_label_item_data in self.frequencies_by_date_by_label:
                frequencies_by_date_by_label_item = frequencies_by_date_by_label_item_data

                frequencies_by_date_by_label.append(frequencies_by_date_by_label_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dates_milliseconds is not UNSET:
            field_dict["datesMilliseconds"] = dates_milliseconds
        if labels is not UNSET:
            field_dict["labels"] = labels
        if frequencies_by_date_by_label is not UNSET:
            field_dict["frequenciesByDateByLabel"] = frequencies_by_date_by_label

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dates_milliseconds = cast(List[int], d.pop("datesMilliseconds", UNSET))

        labels = cast(List[str], d.pop("labels", UNSET))

        frequencies_by_date_by_label = []
        _frequencies_by_date_by_label = d.pop("frequenciesByDateByLabel", UNSET)
        for frequencies_by_date_by_label_item_data in _frequencies_by_date_by_label or []:
            frequencies_by_date_by_label_item = cast(
                List[int], frequencies_by_date_by_label_item_data
            )

            frequencies_by_date_by_label.append(frequencies_by_date_by_label_item)

        label_frequencies_grouped_by_time = cls(
            dates_milliseconds=dates_milliseconds,
            labels=labels,
            frequencies_by_date_by_label=frequencies_by_date_by_label,
        )

        label_frequencies_grouped_by_time.additional_properties = d
        return label_frequencies_grouped_by_time

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
