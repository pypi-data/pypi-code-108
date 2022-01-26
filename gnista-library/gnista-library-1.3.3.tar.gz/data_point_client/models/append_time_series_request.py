from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.sub_series_request import SubSeriesRequest

T = TypeVar("T", bound="AppendTimeSeriesRequest")


@attr.s(auto_attribs=True)
class AppendTimeSeriesRequest:
    """ """

    sub_series: List[SubSeriesRequest]
    part_id: str
    unit: str

    def to_dict(self) -> Dict[str, Any]:
        sub_series = []
        for sub_series_item_data in self.sub_series:
            sub_series_item = sub_series_item_data.to_dict()

            sub_series.append(sub_series_item)

        part_id = self.part_id
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "subSeries": sub_series,
                "partId": part_id,
                "unit": unit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sub_series = []
        _sub_series = d.pop("subSeries")
        for sub_series_item_data in _sub_series:
            sub_series_item = SubSeriesRequest.from_dict(sub_series_item_data)

            sub_series.append(sub_series_item)

        part_id = d.pop("partId")

        unit = d.pop("unit")

        append_time_series_request = cls(
            sub_series=sub_series,
            part_id=part_id,
            unit=unit,
        )

        return append_time_series_request
