from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.stationarisation_strategy import StationarisationStrategy
from ..models.target_transform_type import TargetTransformType
from ..types import UNSET, Unset

T = TypeVar("T", bound="StationarisationStageConfig")


@attr.s(auto_attribs=True)
class StationarisationStageConfig:
    """ Properties for a stage  """

    adf_threshold: float
    strategy: StationarisationStrategy
    target_transform: TargetTransformType
    type: Union[Unset, str] = "stationarisation"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        adf_threshold = self.adf_threshold
        strategy = self.strategy.value

        target_transform = self.target_transform.value

        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "adfThreshold": adf_threshold,
                "strategy": strategy,
                "targetTransform": target_transform,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        adf_threshold = d.pop("adfThreshold")

        strategy = StationarisationStrategy(d.pop("strategy"))

        target_transform = TargetTransformType(d.pop("targetTransform"))

        type = d.pop("type", UNSET)

        stationarisation_stage_config = cls(
            adf_threshold=adf_threshold,
            strategy=strategy,
            target_transform=target_transform,
            type=type,
        )

        stationarisation_stage_config.additional_properties = d
        return stationarisation_stage_config

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
