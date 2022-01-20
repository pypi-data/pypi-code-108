from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="FeatureImportance")


@attr.s(auto_attribs=True)
class FeatureImportance:
    """  """

    feature_name: str
    feature_importance: float
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        feature_name = self.feature_name
        feature_importance = self.feature_importance

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "featureName": feature_name,
                "featureImportance": feature_importance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        feature_name = d.pop("featureName")

        feature_importance = d.pop("featureImportance")

        feature_importance = cls(
            feature_name=feature_name,
            feature_importance=feature_importance,
        )

        feature_importance.additional_properties = d
        return feature_importance

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
