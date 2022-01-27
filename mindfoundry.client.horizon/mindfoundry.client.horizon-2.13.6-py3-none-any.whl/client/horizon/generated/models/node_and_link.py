from typing import Any, Dict, List, Type, TypeVar, cast

import attr

from ..models.feature_transform import FeatureTransform

T = TypeVar("T", bound="NodeAndLink")


@attr.s(auto_attribs=True)
class NodeAndLink:
    """A graph representation of features. Each feature is a node.
    Each edge is a transformation to compute a feature from other features"""

    feature_id: str
    name: str
    horizon: int
    active: bool
    original_column_names: List[str]
    original_column_ids: List[str]
    immediate_parent_ids: List[str]
    transform: FeatureTransform
    pearson_correlation_with_target: float
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        feature_id = self.feature_id
        name = self.name
        horizon = self.horizon
        active = self.active
        original_column_names = self.original_column_names

        original_column_ids = self.original_column_ids

        immediate_parent_ids = self.immediate_parent_ids

        transform = self.transform.to_dict()

        pearson_correlation_with_target = self.pearson_correlation_with_target

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "featureId": feature_id,
                "name": name,
                "horizon": horizon,
                "active": active,
                "originalColumnNames": original_column_names,
                "originalColumnIds": original_column_ids,
                "immediateParentIds": immediate_parent_ids,
                "transform": transform,
                "pearsonCorrelationWithTarget": pearson_correlation_with_target,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        feature_id = d.pop("featureId")

        name = d.pop("name")

        horizon = d.pop("horizon")

        active = d.pop("active")

        original_column_names = cast(List[str], d.pop("originalColumnNames"))

        original_column_ids = cast(List[str], d.pop("originalColumnIds"))

        immediate_parent_ids = cast(List[str], d.pop("immediateParentIds"))

        transform = FeatureTransform.from_dict(d.pop("transform"))

        pearson_correlation_with_target = d.pop("pearsonCorrelationWithTarget")

        node_and_link = cls(
            feature_id=feature_id,
            name=name,
            horizon=horizon,
            active=active,
            original_column_names=original_column_names,
            original_column_ids=original_column_ids,
            immediate_parent_ids=immediate_parent_ids,
            transform=transform,
            pearson_correlation_with_target=pearson_correlation_with_target,
        )

        node_and_link.additional_properties = d
        return node_and_link

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
