from typing import Any, Dict, List, Type, TypeVar, cast

import attr

from ..models.feature_transform_params import FeatureTransformParams

T = TypeVar("T", bound="FeatureTransform")


@attr.s(auto_attribs=True)
class FeatureTransform:
    """  """

    secondary_parameters: List[str]
    transform_category: str
    params: FeatureTransformParams
    explanation: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        secondary_parameters = self.secondary_parameters

        transform_category = self.transform_category
        params = self.params.to_dict()

        explanation = self.explanation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "secondaryParameters": secondary_parameters,
                "transformCategory": transform_category,
                "params": params,
                "explanation": explanation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        secondary_parameters = cast(List[str], d.pop("secondaryParameters"))

        transform_category = d.pop("transformCategory")

        params = FeatureTransformParams.from_dict(d.pop("params"))

        explanation = d.pop("explanation")

        feature_transform = cls(
            secondary_parameters=secondary_parameters,
            transform_category=transform_category,
            params=params,
            explanation=explanation,
        )

        feature_transform.additional_properties = d
        return feature_transform

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
