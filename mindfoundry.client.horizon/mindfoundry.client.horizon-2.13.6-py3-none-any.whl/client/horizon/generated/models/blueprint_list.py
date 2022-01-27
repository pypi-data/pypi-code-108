from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.blueprint_return_object import BlueprintReturnObject

T = TypeVar("T", bound="BlueprintList")


@attr.s(auto_attribs=True)
class BlueprintList:
    """  """

    blueprints: List[BlueprintReturnObject]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        blueprints = []
        for blueprints_item_data in self.blueprints:
            blueprints_item = blueprints_item_data.to_dict()

            blueprints.append(blueprints_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "blueprints": blueprints,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        blueprints = []
        _blueprints = d.pop("blueprints")
        for blueprints_item_data in _blueprints:
            blueprints_item = BlueprintReturnObject.from_dict(blueprints_item_data)

            blueprints.append(blueprints_item)

        blueprint_list = cls(
            blueprints=blueprints,
        )

        blueprint_list.additional_properties = d
        return blueprint_list

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
