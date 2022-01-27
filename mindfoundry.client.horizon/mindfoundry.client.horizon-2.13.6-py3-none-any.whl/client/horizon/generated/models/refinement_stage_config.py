from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.regressor_type import RegressorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RefinementStageConfig")


@attr.s(auto_attribs=True)
class RefinementStageConfig:
    """ Properties for a stage  """

    min_features: int
    max_features: int
    early_stopping_sensitivity: float
    deep_search: bool
    regressor: RegressorType
    type: Union[Unset, str] = "refinement"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        min_features = self.min_features
        max_features = self.max_features
        early_stopping_sensitivity = self.early_stopping_sensitivity
        deep_search = self.deep_search
        regressor = self.regressor.value

        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "minFeatures": min_features,
                "maxFeatures": max_features,
                "earlyStoppingSensitivity": early_stopping_sensitivity,
                "deepSearch": deep_search,
                "regressor": regressor,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        min_features = d.pop("minFeatures")

        max_features = d.pop("maxFeatures")

        early_stopping_sensitivity = d.pop("earlyStoppingSensitivity")

        deep_search = d.pop("deepSearch")

        regressor = RegressorType(d.pop("regressor"))

        type = d.pop("type", UNSET)

        refinement_stage_config = cls(
            min_features=min_features,
            max_features=max_features,
            early_stopping_sensitivity=early_stopping_sensitivity,
            deep_search=deep_search,
            regressor=regressor,
            type=type,
        )

        refinement_stage_config.additional_properties = d
        return refinement_stage_config

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
