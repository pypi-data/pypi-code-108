from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassificationSpecificationConfig")


@attr.s(auto_attribs=True)
class ClassificationSpecificationConfig:
    """ Properties for a stage  """

    target_id: str
    label_to_predict: str
    active_columns: List[int]
    last_train_timestamp_millisec: Union[Unset, None, int] = UNSET
    type: Union[Unset, str] = "classification_specification"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_id = self.target_id
        label_to_predict = self.label_to_predict
        active_columns = self.active_columns

        last_train_timestamp_millisec = self.last_train_timestamp_millisec
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetId": target_id,
                "labelToPredict": label_to_predict,
                "activeColumns": active_columns,
            }
        )
        if last_train_timestamp_millisec is not UNSET:
            field_dict["lastTrainTimestampMillisec"] = last_train_timestamp_millisec
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_id = d.pop("targetId")

        label_to_predict = d.pop("labelToPredict")

        active_columns = cast(List[int], d.pop("activeColumns"))

        last_train_timestamp_millisec = d.pop("lastTrainTimestampMillisec", UNSET)

        type = d.pop("type", UNSET)

        classification_specification_config = cls(
            target_id=target_id,
            label_to_predict=label_to_predict,
            active_columns=active_columns,
            last_train_timestamp_millisec=last_train_timestamp_millisec,
            type=type,
        )

        classification_specification_config.additional_properties = d
        return classification_specification_config

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
