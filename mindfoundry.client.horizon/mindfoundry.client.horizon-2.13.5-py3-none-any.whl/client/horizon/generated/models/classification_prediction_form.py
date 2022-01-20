from io import BytesIO
from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="ClassificationPredictionForm")


@attr.s(auto_attribs=True)
class ClassificationPredictionForm:
    """  """

    target_label: str
    file: Union[Unset, File] = UNSET
    options: Union[Unset, str] = "{}"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_label = self.target_label
        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        options = self.options

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetLabel": target_label,
            }
        )
        if file is not UNSET:
            field_dict["file"] = file
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        target_label = (
            self.target_label
            if self.target_label is UNSET
            else (None, str(self.target_label), "text/plain")
        )
        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        options = (
            self.options if self.options is UNSET else (None, str(self.options), "text/plain")
        )

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                key: (None, str(value), "text/plain")
                for key, value in self.additional_properties.items()
            }
        )
        field_dict.update(
            {
                "targetLabel": target_label,
            }
        )
        if file is not UNSET:
            field_dict["file"] = file
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_label = d.pop("targetLabel")

        _file = d.pop("file", UNSET)
        file: Union[Unset, File]
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = File(payload=BytesIO(_file))

        options = d.pop("options", UNSET)

        classification_prediction_form = cls(
            target_label=target_label,
            file=file,
            options=options,
        )

        classification_prediction_form.additional_properties = d
        return classification_prediction_form

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
