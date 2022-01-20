from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationOutputProcessorArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class AutomationOutputProcessorArchivalChange:
    """ IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of any linked Results that were archived / unarchived. """

    _automation_output_processor_ids: Union[Unset, List[str]] = UNSET
    _result_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append(
            "automation_output_processor_ids={}".format(repr(self._automation_output_processor_ids))
        )
        fields.append("result_ids={}".format(repr(self._result_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AutomationOutputProcessorArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        automation_output_processor_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._automation_output_processor_ids, Unset):
            automation_output_processor_ids = self._automation_output_processor_ids

        result_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._result_ids, Unset):
            result_ids = self._result_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if automation_output_processor_ids is not UNSET:
            field_dict["automationOutputProcessorIds"] = automation_output_processor_ids
        if result_ids is not UNSET:
            field_dict["resultIds"] = result_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_automation_output_processor_ids() -> Union[Unset, List[str]]:
            automation_output_processor_ids = cast(List[str], d.pop("automationOutputProcessorIds"))

            return automation_output_processor_ids

        automation_output_processor_ids = (
            get_automation_output_processor_ids()
            if "automationOutputProcessorIds" in d
            else cast(Union[Unset, List[str]], UNSET)
        )

        def get_result_ids() -> Union[Unset, List[str]]:
            result_ids = cast(List[str], d.pop("resultIds"))

            return result_ids

        result_ids = get_result_ids() if "resultIds" in d else cast(Union[Unset, List[str]], UNSET)

        automation_output_processor_archival_change = cls(
            automation_output_processor_ids=automation_output_processor_ids,
            result_ids=result_ids,
        )

        automation_output_processor_archival_change.additional_properties = d
        return automation_output_processor_archival_change

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def automation_output_processor_ids(self) -> List[str]:
        if isinstance(self._automation_output_processor_ids, Unset):
            raise NotPresentError(self, "automation_output_processor_ids")
        return self._automation_output_processor_ids

    @automation_output_processor_ids.setter
    def automation_output_processor_ids(self, value: List[str]) -> None:
        self._automation_output_processor_ids = value

    @automation_output_processor_ids.deleter
    def automation_output_processor_ids(self) -> None:
        self._automation_output_processor_ids = UNSET

    @property
    def result_ids(self) -> List[str]:
        if isinstance(self._result_ids, Unset):
            raise NotPresentError(self, "result_ids")
        return self._result_ids

    @result_ids.setter
    def result_ids(self, value: List[str]) -> None:
        self._result_ids = value

    @result_ids.deleter
    def result_ids(self) -> None:
        self._result_ids = UNSET
