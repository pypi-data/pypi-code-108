from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.pipeline import Pipeline

T = TypeVar("T", bound="PipelineList")


@attr.s(auto_attribs=True)
class PipelineList:
    """  """

    pipelines: List[Pipeline]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pipelines = []
        for pipelines_item_data in self.pipelines:
            pipelines_item = pipelines_item_data.to_dict()

            pipelines.append(pipelines_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pipelines": pipelines,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipelines = []
        _pipelines = d.pop("pipelines")
        for pipelines_item_data in _pipelines:
            pipelines_item = Pipeline.from_dict(pipelines_item_data)

            pipelines.append(pipelines_item)

        pipeline_list = cls(
            pipelines=pipelines,
        )

        pipeline_list.additional_properties = d
        return pipeline_list

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
