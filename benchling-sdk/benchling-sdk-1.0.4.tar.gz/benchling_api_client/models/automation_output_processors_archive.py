from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.automation_output_processors_archive_reason import AutomationOutputProcessorsArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationOutputProcessorsArchive")


@attr.s(auto_attribs=True, repr=False)
class AutomationOutputProcessorsArchive:
    """  """

    _automation_output_processor_ids: List[str]
    _reason: Union[Unset, AutomationOutputProcessorsArchiveReason] = UNSET

    def __repr__(self):
        fields = []
        fields.append(
            "automation_output_processor_ids={}".format(repr(self._automation_output_processor_ids))
        )
        fields.append("reason={}".format(repr(self._reason)))
        return "AutomationOutputProcessorsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        automation_output_processor_ids = self._automation_output_processor_ids

        reason: Union[Unset, int] = UNSET
        if not isinstance(self._reason, Unset):
            reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "automationOutputProcessorIds": automation_output_processor_ids,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason

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

        def get_reason() -> Union[Unset, AutomationOutputProcessorsArchiveReason]:
            reason = None
            _reason = d.pop("reason")
            if _reason is not None and _reason is not UNSET:
                try:
                    reason = AutomationOutputProcessorsArchiveReason(_reason)
                except ValueError:
                    reason = AutomationOutputProcessorsArchiveReason.of_unknown(_reason)

            return reason

        reason = (
            get_reason()
            if "reason" in d
            else cast(Union[Unset, AutomationOutputProcessorsArchiveReason], UNSET)
        )

        automation_output_processors_archive = cls(
            automation_output_processor_ids=automation_output_processor_ids,
            reason=reason,
        )

        return automation_output_processors_archive

    @property
    def automation_output_processor_ids(self) -> List[str]:
        """ Array of automation output processor IDs """
        if isinstance(self._automation_output_processor_ids, Unset):
            raise NotPresentError(self, "automation_output_processor_ids")
        return self._automation_output_processor_ids

    @automation_output_processor_ids.setter
    def automation_output_processor_ids(self, value: List[str]) -> None:
        self._automation_output_processor_ids = value

    @property
    def reason(self) -> AutomationOutputProcessorsArchiveReason:
        """The reason that the output processors are being archived. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: AutomationOutputProcessorsArchiveReason) -> None:
        self._reason = value

    @reason.deleter
    def reason(self) -> None:
        self._reason = UNSET
