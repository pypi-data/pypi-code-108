from typing import Any, Dict, List, Type, TypeVar, cast

import attr

T = TypeVar("T", bound="PredictionsDTORegressorimportances")


@attr.s(auto_attribs=True)
class PredictionsDTORegressorimportances:
    """ key = feature id, value = feature importances for each prediction row """

    additional_properties: Dict[str, List[float]] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        predictions_dto_regressorimportances = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = cast(List[float], prop_dict)

            additional_properties[prop_name] = additional_property

        predictions_dto_regressorimportances.additional_properties = additional_properties
        return predictions_dto_regressorimportances

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> List[float]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: List[float]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
