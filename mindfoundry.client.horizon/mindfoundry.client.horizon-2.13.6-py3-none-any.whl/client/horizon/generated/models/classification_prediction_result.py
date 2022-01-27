from typing import Any, Dict, List, Type, TypeVar, cast

import attr

from ..models.feature_importance import FeatureImportance

T = TypeVar("T", bound="ClassificationPredictionResult")


@attr.s(auto_attribs=True)
class ClassificationPredictionResult:
    """ The result of a single batch of binary classification predictions  """

    desired_label: str
    dates_timestamp_milliseconds: List[int]
    prediction_pseudo_probabilities: List[float]
    predictions: List[bool]
    feature_importances: List[FeatureImportance]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        desired_label = self.desired_label
        dates_timestamp_milliseconds = self.dates_timestamp_milliseconds

        prediction_pseudo_probabilities = self.prediction_pseudo_probabilities

        predictions = self.predictions

        feature_importances = []
        for feature_importances_item_data in self.feature_importances:
            feature_importances_item = feature_importances_item_data.to_dict()

            feature_importances.append(feature_importances_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "desiredLabel": desired_label,
                "datesTimestampMilliseconds": dates_timestamp_milliseconds,
                "predictionPseudoProbabilities": prediction_pseudo_probabilities,
                "predictions": predictions,
                "featureImportances": feature_importances,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        desired_label = d.pop("desiredLabel")

        dates_timestamp_milliseconds = cast(List[int], d.pop("datesTimestampMilliseconds"))

        prediction_pseudo_probabilities = cast(List[float], d.pop("predictionPseudoProbabilities"))

        predictions = cast(List[bool], d.pop("predictions"))

        feature_importances = []
        _feature_importances = d.pop("featureImportances")
        for feature_importances_item_data in _feature_importances:
            feature_importances_item = FeatureImportance.from_dict(feature_importances_item_data)

            feature_importances.append(feature_importances_item)

        classification_prediction_result = cls(
            desired_label=desired_label,
            dates_timestamp_milliseconds=dates_timestamp_milliseconds,
            prediction_pseudo_probabilities=prediction_pseudo_probabilities,
            predictions=predictions,
            feature_importances=feature_importances,
        )

        classification_prediction_result.additional_properties = d
        return classification_prediction_result

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
