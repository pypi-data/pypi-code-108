from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.backtest_mode import BacktestMode
from ..models.classification_score_metric import ClassificationScoreMetric
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassificationBacktestConfig")


@attr.s(auto_attribs=True)
class ClassificationBacktestConfig:
    """ Properties for a stage  """

    backtest_mode: BacktestMode
    scale_factor: float
    score_metric_type: ClassificationScoreMetric
    start_timestamp_milliseconds: Union[Unset, None, int] = UNSET
    stop_timestamp_milliseconds: Union[Unset, None, int] = UNSET
    type: Union[Unset, str] = "classification_backtest"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        backtest_mode = self.backtest_mode.value

        scale_factor = self.scale_factor
        score_metric_type = self.score_metric_type.value

        start_timestamp_milliseconds = self.start_timestamp_milliseconds
        stop_timestamp_milliseconds = self.stop_timestamp_milliseconds
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "backtestMode": backtest_mode,
                "scaleFactor": scale_factor,
                "scoreMetricType": score_metric_type,
            }
        )
        if start_timestamp_milliseconds is not UNSET:
            field_dict["startTimestampMilliseconds"] = start_timestamp_milliseconds
        if stop_timestamp_milliseconds is not UNSET:
            field_dict["stopTimestampMilliseconds"] = stop_timestamp_milliseconds
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        backtest_mode = BacktestMode(d.pop("backtestMode"))

        scale_factor = d.pop("scaleFactor")

        score_metric_type = ClassificationScoreMetric(d.pop("scoreMetricType"))

        start_timestamp_milliseconds = d.pop("startTimestampMilliseconds", UNSET)

        stop_timestamp_milliseconds = d.pop("stopTimestampMilliseconds", UNSET)

        type = d.pop("type", UNSET)

        classification_backtest_config = cls(
            backtest_mode=backtest_mode,
            scale_factor=scale_factor,
            score_metric_type=score_metric_type,
            start_timestamp_milliseconds=start_timestamp_milliseconds,
            stop_timestamp_milliseconds=stop_timestamp_milliseconds,
            type=type,
        )

        classification_backtest_config.additional_properties = d
        return classification_backtest_config

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
