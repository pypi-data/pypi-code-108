from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.pandas_series import PandasSeries
from ..models.predictions_dto_regressorimportances import PredictionsDTORegressorimportances

T = TypeVar("T", bound="PredictionsDTO")


@attr.s(auto_attribs=True)
class PredictionsDTO:
    """  """

    mean: PandasSeries
    cb_low: PandasSeries
    cb_high: PandasSeries
    confidence: float
    regressor_importances: PredictionsDTORegressorimportances
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        mean = self.mean.to_dict()

        cb_low = self.cb_low.to_dict()

        cb_high = self.cb_high.to_dict()

        confidence = self.confidence
        regressor_importances = self.regressor_importances.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mean": mean,
                "cbLow": cb_low,
                "cbHigh": cb_high,
                "confidence": confidence,
                "regressorImportances": regressor_importances,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mean = PandasSeries.from_dict(d.pop("mean"))

        cb_low = PandasSeries.from_dict(d.pop("cbLow"))

        cb_high = PandasSeries.from_dict(d.pop("cbHigh"))

        confidence = d.pop("confidence")

        regressor_importances = PredictionsDTORegressorimportances.from_dict(
            d.pop("regressorImportances")
        )

        predictions_dto = cls(
            mean=mean,
            cb_low=cb_low,
            cb_high=cb_high,
            confidence=confidence,
            regressor_importances=regressor_importances,
        )

        predictions_dto.additional_properties = d
        return predictions_dto

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
