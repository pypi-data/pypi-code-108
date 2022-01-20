from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationOutputProcessorsUnarchive")


@attr.s(auto_attribs=True, repr=False)
class AutomationOutputProcessorsUnarchive:
    """  """

    _automation_output_processor_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append(
            "automation_output_processor_ids={}".format(repr(self._automation_output_processor_ids))
        )
        return "AutomationOutputProcessorsUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        automation_output_processor_ids = self._automation_output_processor_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "automationOutputProcessorIds": automation_output_processor_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_automation_output_processor_ids() -> List[str]:
            automation_output_processor_ids = cast(List[str], d.pop("automationOutputProcessorIds"))

            return automation_output_processor_ids

        automation_output_processor_ids = (
            get_automation_output_processor_ids()
            if "automationOutputProcessorIds" in d
            else cast(List[str], UNSET)
        )

        automation_output_processors_unarchive = cls(
            automation_output_processor_ids=automation_output_processor_ids,
        )

        return automation_output_processors_unarchive

    @property
    def automation_output_processor_ids(self) -> List[str]:
        """ Array of automation output processor IDs """
        if isinstance(self._automation_output_processor_ids, Unset):
            raise NotPresentError(self, "automation_output_processor_ids")
        return self._automation_output_processor_ids

    @automation_output_processor_ids.setter
    def automation_output_processor_ids(self, value: List[str]) -> None:
        self._automation_output_processor_ids = value
