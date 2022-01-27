from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.stage_type import StageType

T = TypeVar("T", bound="BlueprintStageReturnObject")


@attr.s(auto_attribs=True)
class BlueprintStageReturnObject:
    """  """

    stage: StageType
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        stage = self.stage.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stage": stage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        stage = StageType(d.pop("stage"))

        blueprint_stage_return_object = cls(
            stage=stage,
        )

        blueprint_stage_return_object.additional_properties = d
        return blueprint_stage_return_object

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
