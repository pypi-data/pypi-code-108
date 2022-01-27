from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.classification_score_metric import ClassificationScoreMetric

T = TypeVar("T", bound="SummaryScoreMetric")


@attr.s(auto_attribs=True)
class SummaryScoreMetric:
    """  """

    target_label: str
    type: ClassificationScoreMetric
    value: float
    best_possible_score: float
    worst_possible_score: float
    naive_model_expected_value: float
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_label = self.target_label
        type = self.type.value

        value = self.value
        best_possible_score = self.best_possible_score
        worst_possible_score = self.worst_possible_score
        naive_model_expected_value = self.naive_model_expected_value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetLabel": target_label,
                "type": type,
                "value": value,
                "bestPossibleScore": best_possible_score,
                "worstPossibleScore": worst_possible_score,
                "naiveModelExpectedValue": naive_model_expected_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_label = d.pop("targetLabel")

        type = ClassificationScoreMetric(d.pop("type"))

        value = d.pop("value")

        best_possible_score = d.pop("bestPossibleScore")

        worst_possible_score = d.pop("worstPossibleScore")

        naive_model_expected_value = d.pop("naiveModelExpectedValue")

        summary_score_metric = cls(
            target_label=target_label,
            type=type,
            value=value,
            best_possible_score=best_possible_score,
            worst_possible_score=worst_possible_score,
            naive_model_expected_value=naive_model_expected_value,
        )

        summary_score_metric.additional_properties = d
        return summary_score_metric

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
