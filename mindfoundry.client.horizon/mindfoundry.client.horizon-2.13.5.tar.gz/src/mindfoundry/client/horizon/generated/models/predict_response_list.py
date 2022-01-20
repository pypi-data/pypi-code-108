from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.predict_response import PredictResponse

T = TypeVar("T", bound="PredictResponseList")


@attr.s(auto_attribs=True)
class PredictResponseList:
    """  """

    predict_responses: List[PredictResponse]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        predict_responses = []
        for predict_responses_item_data in self.predict_responses:
            predict_responses_item = predict_responses_item_data.to_dict()

            predict_responses.append(predict_responses_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "predictResponses": predict_responses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        predict_responses = []
        _predict_responses = d.pop("predictResponses")
        for predict_responses_item_data in _predict_responses:
            predict_responses_item = PredictResponse.from_dict(predict_responses_item_data)

            predict_responses.append(predict_responses_item)

        predict_response_list = cls(
            predict_responses=predict_responses,
        )

        predict_response_list.additional_properties = d
        return predict_response_list

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
