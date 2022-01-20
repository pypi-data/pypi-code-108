from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.predictions_dto import PredictionsDTO

T = TypeVar("T", bound="PredictResponse")


@attr.s(auto_attribs=True)
class PredictResponse:
    """  """

    target_original_column_name: str
    predictions: PredictionsDTO
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_original_column_name = self.target_original_column_name
        predictions = self.predictions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetOriginalColumnName": target_original_column_name,
                "predictions": predictions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_original_column_name = d.pop("targetOriginalColumnName")

        predictions = PredictionsDTO.from_dict(d.pop("predictions"))

        predict_response = cls(
            target_original_column_name=target_original_column_name,
            predictions=predictions,
        )

        predict_response.additional_properties = d
        return predict_response

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
