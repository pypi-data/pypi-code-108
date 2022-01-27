from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.feature_generator_type import FeatureGeneratorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureGenerationStageConfig")


@attr.s(auto_attribs=True)
class FeatureGenerationStageConfig:
    """ Properties for a stage  """

    max_n_features: int
    feature_generators: List[FeatureGeneratorType]
    type: Union[Unset, str] = "feature_generation"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        max_n_features = self.max_n_features
        feature_generators = []
        for feature_generators_item_data in self.feature_generators:
            feature_generators_item = feature_generators_item_data.value

            feature_generators.append(feature_generators_item)

        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "maxNFeatures": max_n_features,
                "featureGenerators": feature_generators,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        max_n_features = d.pop("maxNFeatures")

        feature_generators = []
        _feature_generators = d.pop("featureGenerators")
        for feature_generators_item_data in _feature_generators:
            feature_generators_item = FeatureGeneratorType(feature_generators_item_data)

            feature_generators.append(feature_generators_item)

        type = d.pop("type", UNSET)

        feature_generation_stage_config = cls(
            max_n_features=max_n_features,
            feature_generators=feature_generators,
            type=type,
        )

        feature_generation_stage_config.additional_properties = d
        return feature_generation_stage_config

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
