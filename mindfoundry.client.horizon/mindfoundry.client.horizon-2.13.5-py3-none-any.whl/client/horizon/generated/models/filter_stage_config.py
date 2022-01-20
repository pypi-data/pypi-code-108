from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.correlation_method import CorrelationMethod
from ..types import UNSET, Unset

T = TypeVar("T", bound="FilterStageConfig")


@attr.s(auto_attribs=True)
class FilterStageConfig:
    """ Properties for a stage  """

    max_n_features: int
    method: CorrelationMethod
    type: Union[Unset, str] = "filtering"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        max_n_features = self.max_n_features
        method = self.method.value

        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "maxNFeatures": max_n_features,
                "method": method,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        max_n_features = d.pop("maxNFeatures")

        method = CorrelationMethod(d.pop("method"))

        type = d.pop("type", UNSET)

        filter_stage_config = cls(
            max_n_features=max_n_features,
            method=method,
            type=type,
        )

        filter_stage_config.additional_properties = d
        return filter_stage_config

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
