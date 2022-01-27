from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.classification_score_metric import ClassificationScoreMetric
from ..models.feature_importance import FeatureImportance
from ..models.summary_score_metric import SummaryScoreMetric
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassificationBacktestInsight")


@attr.s(auto_attribs=True)
class ClassificationBacktestInsight:
    """Information generated as a side effect of running a stage, detailing
    intermediate results and analyses used to define which features were output from the
    stage."""

    target_label_to_detect: str
    summary_score_metrics: List[SummaryScoreMetric]
    summary_predicted_true_actual_true: int
    summary_predicted_true_actual_false: int
    summary_predicted_false_actual_true: int
    summary_predicted_false_actual_false: int
    average_feature_importances: List[FeatureImportance]
    rolling_score_metric_type: ClassificationScoreMetric
    dates_timestamp_milliseconds: Union[Unset, List[int]] = UNSET
    rolling_score_metric_values: Union[Unset, List[float]] = UNSET
    prediction_pseudo_probabilities: Union[Unset, List[float]] = UNSET
    predictions: Union[Unset, List[bool]] = UNSET
    ground_truths: Union[Unset, List[bool]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_label_to_detect = self.target_label_to_detect
        summary_score_metrics = []
        for summary_score_metrics_item_data in self.summary_score_metrics:
            summary_score_metrics_item = summary_score_metrics_item_data.to_dict()

            summary_score_metrics.append(summary_score_metrics_item)

        summary_predicted_true_actual_true = self.summary_predicted_true_actual_true
        summary_predicted_true_actual_false = self.summary_predicted_true_actual_false
        summary_predicted_false_actual_true = self.summary_predicted_false_actual_true
        summary_predicted_false_actual_false = self.summary_predicted_false_actual_false
        average_feature_importances = []
        for average_feature_importances_item_data in self.average_feature_importances:
            average_feature_importances_item = average_feature_importances_item_data.to_dict()

            average_feature_importances.append(average_feature_importances_item)

        rolling_score_metric_type = self.rolling_score_metric_type.value

        dates_timestamp_milliseconds: Union[Unset, List[int]] = UNSET
        if not isinstance(self.dates_timestamp_milliseconds, Unset):
            dates_timestamp_milliseconds = self.dates_timestamp_milliseconds

        rolling_score_metric_values: Union[Unset, List[float]] = UNSET
        if not isinstance(self.rolling_score_metric_values, Unset):
            rolling_score_metric_values = self.rolling_score_metric_values

        prediction_pseudo_probabilities: Union[Unset, List[float]] = UNSET
        if not isinstance(self.prediction_pseudo_probabilities, Unset):
            prediction_pseudo_probabilities = self.prediction_pseudo_probabilities

        predictions: Union[Unset, List[bool]] = UNSET
        if not isinstance(self.predictions, Unset):
            predictions = self.predictions

        ground_truths: Union[Unset, List[bool]] = UNSET
        if not isinstance(self.ground_truths, Unset):
            ground_truths = self.ground_truths

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetLabelToDetect": target_label_to_detect,
                "summaryScoreMetrics": summary_score_metrics,
                "summaryPredictedTrueActualTrue": summary_predicted_true_actual_true,
                "summaryPredictedTrueActualFalse": summary_predicted_true_actual_false,
                "summaryPredictedFalseActualTrue": summary_predicted_false_actual_true,
                "summaryPredictedFalseActualFalse": summary_predicted_false_actual_false,
                "averageFeatureImportances": average_feature_importances,
                "rollingScoreMetricType": rolling_score_metric_type,
            }
        )
        if dates_timestamp_milliseconds is not UNSET:
            field_dict["datesTimestampMilliseconds"] = dates_timestamp_milliseconds
        if rolling_score_metric_values is not UNSET:
            field_dict["rollingScoreMetricValues"] = rolling_score_metric_values
        if prediction_pseudo_probabilities is not UNSET:
            field_dict["predictionPseudoProbabilities"] = prediction_pseudo_probabilities
        if predictions is not UNSET:
            field_dict["predictions"] = predictions
        if ground_truths is not UNSET:
            field_dict["groundTruths"] = ground_truths

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_label_to_detect = d.pop("targetLabelToDetect")

        summary_score_metrics = []
        _summary_score_metrics = d.pop("summaryScoreMetrics")
        for summary_score_metrics_item_data in _summary_score_metrics:
            summary_score_metrics_item = SummaryScoreMetric.from_dict(
                summary_score_metrics_item_data
            )

            summary_score_metrics.append(summary_score_metrics_item)

        summary_predicted_true_actual_true = d.pop("summaryPredictedTrueActualTrue")

        summary_predicted_true_actual_false = d.pop("summaryPredictedTrueActualFalse")

        summary_predicted_false_actual_true = d.pop("summaryPredictedFalseActualTrue")

        summary_predicted_false_actual_false = d.pop("summaryPredictedFalseActualFalse")

        average_feature_importances = []
        _average_feature_importances = d.pop("averageFeatureImportances")
        for average_feature_importances_item_data in _average_feature_importances:
            average_feature_importances_item = FeatureImportance.from_dict(
                average_feature_importances_item_data
            )

            average_feature_importances.append(average_feature_importances_item)

        rolling_score_metric_type = ClassificationScoreMetric(d.pop("rollingScoreMetricType"))

        dates_timestamp_milliseconds = cast(List[int], d.pop("datesTimestampMilliseconds", UNSET))

        rolling_score_metric_values = cast(List[float], d.pop("rollingScoreMetricValues", UNSET))

        prediction_pseudo_probabilities = cast(
            List[float], d.pop("predictionPseudoProbabilities", UNSET)
        )

        predictions = cast(List[bool], d.pop("predictions", UNSET))

        ground_truths = cast(List[bool], d.pop("groundTruths", UNSET))

        classification_backtest_insight = cls(
            target_label_to_detect=target_label_to_detect,
            summary_score_metrics=summary_score_metrics,
            summary_predicted_true_actual_true=summary_predicted_true_actual_true,
            summary_predicted_true_actual_false=summary_predicted_true_actual_false,
            summary_predicted_false_actual_true=summary_predicted_false_actual_true,
            summary_predicted_false_actual_false=summary_predicted_false_actual_false,
            average_feature_importances=average_feature_importances,
            rolling_score_metric_type=rolling_score_metric_type,
            dates_timestamp_milliseconds=dates_timestamp_milliseconds,
            rolling_score_metric_values=rolling_score_metric_values,
            prediction_pseudo_probabilities=prediction_pseudo_probabilities,
            predictions=predictions,
            ground_truths=ground_truths,
        )

        classification_backtest_insight.additional_properties = d
        return classification_backtest_insight

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
