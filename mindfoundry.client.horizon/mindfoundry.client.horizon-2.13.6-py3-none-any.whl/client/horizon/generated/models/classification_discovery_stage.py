from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.classification_discovery_config import ClassificationDiscoveryConfig
from ..models.stage_status import StageStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassificationDiscoveryStage")


@attr.s(auto_attribs=True)
class ClassificationDiscoveryStage:
    """Stage for discovering data transformations that might help the classifier

    The stage data will contain the discovered transformations, so other stages can use
    them.

    This Stage is like 'Feature Generation' in regression pipelines, but more flexible,
    allowing for dual-parent features as well as single-parent features."""

    status: StageStatus
    id: int
    config: ClassificationDiscoveryConfig
    error_msg: Union[Unset, None, str] = UNSET
    type: Union[Unset, str] = "classification_discovery"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        id = self.id
        config = self.config.to_dict()

        error_msg = self.error_msg
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "id": id,
                "config": config,
            }
        )
        if error_msg is not UNSET:
            field_dict["errorMsg"] = error_msg
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = StageStatus(d.pop("status"))

        id = d.pop("id")

        config = ClassificationDiscoveryConfig.from_dict(d.pop("config"))

        error_msg = d.pop("errorMsg", UNSET)

        type = d.pop("type", UNSET)

        classification_discovery_stage = cls(
            status=status,
            id=id,
            config=config,
            error_msg=error_msg,
            type=type,
        )

        classification_discovery_stage.additional_properties = d
        return classification_discovery_stage

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
