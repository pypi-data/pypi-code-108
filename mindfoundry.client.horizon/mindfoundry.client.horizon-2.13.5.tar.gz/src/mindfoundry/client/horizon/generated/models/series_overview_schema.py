from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.date_value_point_schema import DateValuePointSchema
from ..models.label_frequencies_grouped_by_time import LabelFrequenciesGroupedByTime
from ..models.ohlc_point_schema import OHLCPointSchema
from ..models.text_label_counts import TextLabelCounts
from ..types import UNSET, Unset

T = TypeVar("T", bound="SeriesOverviewSchema")


@attr.s(auto_attribs=True)
class SeriesOverviewSchema:
    """  """

    series_name: str
    ohlc_data: List[List[OHLCPointSchema]]
    close_data: List[List[DateValuePointSchema]]
    intraday_available: bool
    text_highest_frequencies: List[TextLabelCounts]
    frequencies_grouped_by_time: Union[Unset, LabelFrequenciesGroupedByTime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        series_name = self.series_name
        ohlc_data = []
        for ohlc_data_item_data in self.ohlc_data:
            ohlc_data_item = []
            for ohlc_data_item_item_data in ohlc_data_item_data:
                ohlc_data_item_item = ohlc_data_item_item_data.to_dict()

                ohlc_data_item.append(ohlc_data_item_item)

            ohlc_data.append(ohlc_data_item)

        close_data = []
        for close_data_item_data in self.close_data:
            close_data_item = []
            for close_data_item_item_data in close_data_item_data:
                close_data_item_item = close_data_item_item_data.to_dict()

                close_data_item.append(close_data_item_item)

            close_data.append(close_data_item)

        intraday_available = self.intraday_available
        text_highest_frequencies = []
        for text_highest_frequencies_item_data in self.text_highest_frequencies:
            text_highest_frequencies_item = text_highest_frequencies_item_data.to_dict()

            text_highest_frequencies.append(text_highest_frequencies_item)

        frequencies_grouped_by_time: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.frequencies_grouped_by_time, Unset):
            frequencies_grouped_by_time = self.frequencies_grouped_by_time.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "seriesName": series_name,
                "ohlcData": ohlc_data,
                "closeData": close_data,
                "intradayAvailable": intraday_available,
                "textHighestFrequencies": text_highest_frequencies,
            }
        )
        if frequencies_grouped_by_time is not UNSET:
            field_dict["frequenciesGroupedByTime"] = frequencies_grouped_by_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        series_name = d.pop("seriesName")

        ohlc_data = []
        _ohlc_data = d.pop("ohlcData")
        for ohlc_data_item_data in _ohlc_data:
            ohlc_data_item = []
            _ohlc_data_item = ohlc_data_item_data
            for ohlc_data_item_item_data in _ohlc_data_item:
                ohlc_data_item_item = OHLCPointSchema.from_dict(ohlc_data_item_item_data)

                ohlc_data_item.append(ohlc_data_item_item)

            ohlc_data.append(ohlc_data_item)

        close_data = []
        _close_data = d.pop("closeData")
        for close_data_item_data in _close_data:
            close_data_item = []
            _close_data_item = close_data_item_data
            for close_data_item_item_data in _close_data_item:
                close_data_item_item = DateValuePointSchema.from_dict(close_data_item_item_data)

                close_data_item.append(close_data_item_item)

            close_data.append(close_data_item)

        intraday_available = d.pop("intradayAvailable")

        text_highest_frequencies = []
        _text_highest_frequencies = d.pop("textHighestFrequencies")
        for text_highest_frequencies_item_data in _text_highest_frequencies:
            text_highest_frequencies_item = TextLabelCounts.from_dict(
                text_highest_frequencies_item_data
            )

            text_highest_frequencies.append(text_highest_frequencies_item)

        _frequencies_grouped_by_time = d.pop("frequenciesGroupedByTime", UNSET)
        frequencies_grouped_by_time: Union[Unset, LabelFrequenciesGroupedByTime]
        if isinstance(_frequencies_grouped_by_time, Unset):
            frequencies_grouped_by_time = UNSET
        else:
            frequencies_grouped_by_time = LabelFrequenciesGroupedByTime.from_dict(
                _frequencies_grouped_by_time
            )

        series_overview_schema = cls(
            series_name=series_name,
            ohlc_data=ohlc_data,
            close_data=close_data,
            intraday_available=intraday_available,
            text_highest_frequencies=text_highest_frequencies,
            frequencies_grouped_by_time=frequencies_grouped_by_time,
        )

        series_overview_schema.additional_properties = d
        return series_overview_schema

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
