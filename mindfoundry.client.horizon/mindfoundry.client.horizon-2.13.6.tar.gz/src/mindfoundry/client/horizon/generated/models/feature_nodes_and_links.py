from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.node_and_link import NodeAndLink

T = TypeVar("T", bound="FeatureNodesAndLinks")


@attr.s(auto_attribs=True)
class FeatureNodesAndLinks:
    """ A representation of a Feature (some transformation of the original data)  """

    stage_id: int
    nodes_and_links: List[NodeAndLink]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        stage_id = self.stage_id
        nodes_and_links = []
        for nodes_and_links_item_data in self.nodes_and_links:
            nodes_and_links_item = nodes_and_links_item_data.to_dict()

            nodes_and_links.append(nodes_and_links_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stageId": stage_id,
                "nodesAndLinks": nodes_and_links,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        stage_id = d.pop("stageId")

        nodes_and_links = []
        _nodes_and_links = d.pop("nodesAndLinks")
        for nodes_and_links_item_data in _nodes_and_links:
            nodes_and_links_item = NodeAndLink.from_dict(nodes_and_links_item_data)

            nodes_and_links.append(nodes_and_links_item)

        feature_nodes_and_links = cls(
            stage_id=stage_id,
            nodes_and_links=nodes_and_links,
        )

        feature_nodes_and_links.additional_properties = d
        return feature_nodes_and_links

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
