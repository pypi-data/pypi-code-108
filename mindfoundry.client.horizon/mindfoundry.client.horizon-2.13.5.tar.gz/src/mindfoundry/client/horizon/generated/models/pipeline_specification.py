from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.blueprint_type import BlueprintType

T = TypeVar("T", bound="PipelineSpecification")


@attr.s(auto_attribs=True)
class PipelineSpecification:
    """  """

    dataset_id: int
    name: str
    blueprint: BlueprintType
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_id = self.dataset_id
        name = self.name
        blueprint = self.blueprint.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datasetId": dataset_id,
                "name": name,
                "blueprint": blueprint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_id = d.pop("datasetId")

        name = d.pop("name")

        blueprint = BlueprintType(d.pop("blueprint"))

        pipeline_specification = cls(
            dataset_id=dataset_id,
            name=name,
            blueprint=blueprint,
        )

        pipeline_specification.additional_properties = d
        return pipeline_specification

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
