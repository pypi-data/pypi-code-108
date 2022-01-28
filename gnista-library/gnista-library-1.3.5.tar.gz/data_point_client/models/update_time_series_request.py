from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.sub_series_request import SubSeriesRequest
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateTimeSeriesRequest")


@attr.s(auto_attribs=True)
class UpdateTimeSeriesRequest:
    """ """

    execution_id: Union[Unset, None, str] = UNSET
    sub_series: Union[Unset, None, List[SubSeriesRequest]] = UNSET
    warnings: Union[Unset, None, List[str]] = UNSET
    unit: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        execution_id = self.execution_id
        sub_series: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sub_series, Unset):
            if self.sub_series is None:
                sub_series = None
            else:
                sub_series = []
                for sub_series_item_data in self.sub_series:
                    sub_series_item = sub_series_item_data.to_dict()

                    sub_series.append(sub_series_item)

        warnings: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.warnings, Unset):
            if self.warnings is None:
                warnings = None
            else:
                warnings = self.warnings

        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if execution_id is not UNSET:
            field_dict["executionId"] = execution_id
        if sub_series is not UNSET:
            field_dict["subSeries"] = sub_series
        if warnings is not UNSET:
            field_dict["warnings"] = warnings
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        execution_id = d.pop("executionId", UNSET)

        sub_series = []
        _sub_series = d.pop("subSeries", UNSET)
        for sub_series_item_data in _sub_series or []:
            sub_series_item = SubSeriesRequest.from_dict(sub_series_item_data)

            sub_series.append(sub_series_item)

        warnings = cast(List[str], d.pop("warnings", UNSET))

        unit = d.pop("unit", UNSET)

        update_time_series_request = cls(
            execution_id=execution_id,
            sub_series=sub_series,
            warnings=warnings,
            unit=unit,
        )

        return update_time_series_request
