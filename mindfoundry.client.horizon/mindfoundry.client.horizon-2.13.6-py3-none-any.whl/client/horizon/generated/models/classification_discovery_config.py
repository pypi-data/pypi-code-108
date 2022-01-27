from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassificationDiscoveryConfig")


@attr.s(auto_attribs=True)
class ClassificationDiscoveryConfig:
    """ Properties for a stage  """

    feature_generation_enabled: bool
    timeout_seconds: float
    columns_to_not_generate_features_from: List[str]
    max_n_features: int
    type: Union[Unset, str] = "classification_discovery"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        feature_generation_enabled = self.feature_generation_enabled
        timeout_seconds = self.timeout_seconds
        columns_to_not_generate_features_from = self.columns_to_not_generate_features_from

        max_n_features = self.max_n_features
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "featureGenerationEnabled": feature_generation_enabled,
                "timeoutSeconds": timeout_seconds,
                "columnsToNotGenerateFeaturesFrom": columns_to_not_generate_features_from,
                "maxNFeatures": max_n_features,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        feature_generation_enabled = d.pop("featureGenerationEnabled")

        timeout_seconds = d.pop("timeoutSeconds")

        columns_to_not_generate_features_from = cast(
            List[str], d.pop("columnsToNotGenerateFeaturesFrom")
        )

        max_n_features = d.pop("maxNFeatures")

        type = d.pop("type", UNSET)

        classification_discovery_config = cls(
            feature_generation_enabled=feature_generation_enabled,
            timeout_seconds=timeout_seconds,
            columns_to_not_generate_features_from=columns_to_not_generate_features_from,
            max_n_features=max_n_features,
            type=type,
        )

        classification_discovery_config.additional_properties = d
        return classification_discovery_config

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
