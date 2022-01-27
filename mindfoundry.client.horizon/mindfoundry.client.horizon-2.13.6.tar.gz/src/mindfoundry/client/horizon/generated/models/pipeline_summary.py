import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

from ..models.blueprint_type import BlueprintType

T = TypeVar("T", bound="PipelineSummary")


@attr.s(auto_attribs=True)
class PipelineSummary:
    """ High level information about a pipeline  """

    id: int
    name: str
    locked: bool
    auto_update: bool
    blueprint: BlueprintType
    creation_date: datetime.datetime
    creation_user: int
    dataset_name: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        locked = self.locked
        auto_update = self.auto_update
        blueprint = self.blueprint.value

        creation_date = self.creation_date.isoformat()

        creation_user = self.creation_user
        dataset_name = self.dataset_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "locked": locked,
                "autoUpdate": auto_update,
                "blueprint": blueprint,
                "creationDate": creation_date,
                "creationUser": creation_user,
                "datasetName": dataset_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        locked = d.pop("locked")

        auto_update = d.pop("autoUpdate")

        blueprint = BlueprintType(d.pop("blueprint"))

        creation_date = isoparse(d.pop("creationDate"))

        creation_user = d.pop("creationUser")

        dataset_name = d.pop("datasetName")

        pipeline_summary = cls(
            id=id,
            name=name,
            locked=locked,
            auto_update=auto_update,
            blueprint=blueprint,
            creation_date=creation_date,
            creation_user=creation_user,
            dataset_name=dataset_name,
        )

        pipeline_summary.additional_properties = d
        return pipeline_summary

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
