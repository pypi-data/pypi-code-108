from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationOutputProcessorCreate")


@attr.s(auto_attribs=True, repr=False)
class AutomationOutputProcessorCreate:
    """  """

    _assay_run_id: str
    _automation_file_config_name: str
    _file_id: str
    _complete_with_errors: Union[Unset, bool] = UNSET

    def __repr__(self):
        fields = []
        fields.append("assay_run_id={}".format(repr(self._assay_run_id)))
        fields.append("automation_file_config_name={}".format(repr(self._automation_file_config_name)))
        fields.append("file_id={}".format(repr(self._file_id)))
        fields.append("complete_with_errors={}".format(repr(self._complete_with_errors)))
        return "AutomationOutputProcessorCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_run_id = self._assay_run_id
        automation_file_config_name = self._automation_file_config_name
        file_id = self._file_id
        complete_with_errors = self._complete_with_errors

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayRunId": assay_run_id,
                "automationFileConfigName": automation_file_config_name,
                "fileId": file_id,
            }
        )
        if complete_with_errors is not UNSET:
            field_dict["completeWithErrors"] = complete_with_errors

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_run_id() -> str:
            assay_run_id = d.pop("assayRunId")
            return assay_run_id

        assay_run_id = get_assay_run_id() if "assayRunId" in d else cast(str, UNSET)

        def get_automation_file_config_name() -> str:
            automation_file_config_name = d.pop("automationFileConfigName")
            return automation_file_config_name

        automation_file_config_name = (
            get_automation_file_config_name() if "automationFileConfigName" in d else cast(str, UNSET)
        )

        def get_file_id() -> str:
            file_id = d.pop("fileId")
            return file_id

        file_id = get_file_id() if "fileId" in d else cast(str, UNSET)

        def get_complete_with_errors() -> Union[Unset, bool]:
            complete_with_errors = d.pop("completeWithErrors")
            return complete_with_errors

        complete_with_errors = (
            get_complete_with_errors() if "completeWithErrors" in d else cast(Union[Unset, bool], UNSET)
        )

        automation_output_processor_create = cls(
            assay_run_id=assay_run_id,
            automation_file_config_name=automation_file_config_name,
            file_id=file_id,
            complete_with_errors=complete_with_errors,
        )

        return automation_output_processor_create

    @property
    def assay_run_id(self) -> str:
        if isinstance(self._assay_run_id, Unset):
            raise NotPresentError(self, "assay_run_id")
        return self._assay_run_id

    @assay_run_id.setter
    def assay_run_id(self, value: str) -> None:
        self._assay_run_id = value

    @property
    def automation_file_config_name(self) -> str:
        if isinstance(self._automation_file_config_name, Unset):
            raise NotPresentError(self, "automation_file_config_name")
        return self._automation_file_config_name

    @automation_file_config_name.setter
    def automation_file_config_name(self, value: str) -> None:
        self._automation_file_config_name = value

    @property
    def file_id(self) -> str:
        """ The ID of a blob link to process. """
        if isinstance(self._file_id, Unset):
            raise NotPresentError(self, "file_id")
        return self._file_id

    @file_id.setter
    def file_id(self, value: str) -> None:
        self._file_id = value

    @property
    def complete_with_errors(self) -> bool:
        """ Specifies whether file processing should complete with errors. False means any error in output file processing will result in no actions being committed. True means that if row-level errors occur, then failing rows and their errors will be saved to errorFile, and actions from successful rows will be committed. """
        if isinstance(self._complete_with_errors, Unset):
            raise NotPresentError(self, "complete_with_errors")
        return self._complete_with_errors

    @complete_with_errors.setter
    def complete_with_errors(self, value: bool) -> None:
        self._complete_with_errors = value

    @complete_with_errors.deleter
    def complete_with_errors(self) -> None:
        self._complete_with_errors = UNSET
