from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.time_series_period import TimeSeriesPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDataRequest")


@attr.s(auto_attribs=True)
class GetDataRequest:
    """ """

    window_hours: Union[Unset, int] = UNSET
    version: Union[Unset, None, int] = UNSET
    time_series_periods: Union[Unset, None, List[TimeSeriesPeriod]] = UNSET
    demanded_unit: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        window_hours = self.window_hours
        version = self.version
        time_series_periods: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.time_series_periods, Unset):
            if self.time_series_periods is None:
                time_series_periods = None
            else:
                time_series_periods = []
                for time_series_periods_item_data in self.time_series_periods:
                    time_series_periods_item = time_series_periods_item_data.to_dict()

                    time_series_periods.append(time_series_periods_item)

        demanded_unit = self.demanded_unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if window_hours is not UNSET:
            field_dict["windowHours"] = window_hours
        if version is not UNSET:
            field_dict["version"] = version
        if time_series_periods is not UNSET:
            field_dict["timeSeriesPeriods"] = time_series_periods
        if demanded_unit is not UNSET:
            field_dict["demandedUnit"] = demanded_unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        window_hours = d.pop("windowHours", UNSET)

        version = d.pop("version", UNSET)

        time_series_periods = []
        _time_series_periods = d.pop("timeSeriesPeriods", UNSET)
        for time_series_periods_item_data in _time_series_periods or []:
            time_series_periods_item = TimeSeriesPeriod.from_dict(time_series_periods_item_data)

            time_series_periods.append(time_series_periods_item)

        demanded_unit = d.pop("demandedUnit", UNSET)

        get_data_request = cls(
            window_hours=window_hours,
            version=version,
            time_series_periods=time_series_periods,
            demanded_unit=demanded_unit,
        )

        return get_data_request
