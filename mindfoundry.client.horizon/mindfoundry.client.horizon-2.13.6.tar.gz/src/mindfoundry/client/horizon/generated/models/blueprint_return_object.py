from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.blueprint_stage_return_object import BlueprintStageReturnObject
from ..models.blueprint_type import BlueprintType

T = TypeVar("T", bound="BlueprintReturnObject")


@attr.s(auto_attribs=True)
class BlueprintReturnObject:
    """  """

    type: BlueprintType
    stages: List[BlueprintStageReturnObject]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        stages = []
        for stages_item_data in self.stages:
            stages_item = stages_item_data.to_dict()

            stages.append(stages_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "stages": stages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = BlueprintType(d.pop("type"))

        stages = []
        _stages = d.pop("stages")
        for stages_item_data in _stages:
            stages_item = BlueprintStageReturnObject.from_dict(stages_item_data)

            stages.append(stages_item)

        blueprint_return_object = cls(
            type=type,
            stages=stages,
        )

        blueprint_return_object.additional_properties = d
        return blueprint_return_object

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
