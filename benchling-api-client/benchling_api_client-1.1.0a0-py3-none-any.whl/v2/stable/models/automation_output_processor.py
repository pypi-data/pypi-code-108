import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.automation_file_automation_file_config import AutomationFileAutomationFileConfig
from ..models.automation_file_status import AutomationFileStatus
from ..models.automation_progress_stats import AutomationProgressStats
from ..models.blob import Blob
from ..models.lab_automation_transform import LabAutomationTransform
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationOutputProcessor")


@attr.s(auto_attribs=True, repr=False)
class AutomationOutputProcessor:
    """  """

    _api_url: Union[Unset, str] = UNSET
    _archive_record: Union[Unset, ArchiveRecord] = UNSET
    _complete_with_errors: Union[Unset, bool] = UNSET
    _error_file: Union[Unset, None, Blob] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _progress_stats: Union[Unset, AutomationProgressStats] = UNSET
    _transforms: Union[Unset, List[LabAutomationTransform]] = UNSET
    _assay_run_id: Union[Unset, str] = UNSET
    _automation_file_config: Union[Unset, AutomationFileAutomationFileConfig] = UNSET
    _file: Union[Unset, None, Blob] = UNSET
    _status: Union[Unset, AutomationFileStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("complete_with_errors={}".format(repr(self._complete_with_errors)))
        fields.append("error_file={}".format(repr(self._error_file)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("progress_stats={}".format(repr(self._progress_stats)))
        fields.append("transforms={}".format(repr(self._transforms)))
        fields.append("assay_run_id={}".format(repr(self._assay_run_id)))
        fields.append("automation_file_config={}".format(repr(self._automation_file_config)))
        fields.append("file={}".format(repr(self._file)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AutomationOutputProcessor({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_url = self._api_url
        archive_record: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict()

        complete_with_errors = self._complete_with_errors
        error_file: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._error_file, Unset):
            error_file = self._error_file.to_dict() if self._error_file else None

        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        progress_stats: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._progress_stats, Unset):
            progress_stats = self._progress_stats.to_dict()

        transforms: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._transforms, Unset):
            transforms = []
            for transforms_item_data in self._transforms:
                transforms_item = transforms_item_data.to_dict()

                transforms.append(transforms_item)

        assay_run_id = self._assay_run_id
        automation_file_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._automation_file_config, Unset):
            automation_file_config = self._automation_file_config.to_dict()

        file: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._file, Unset):
            file = self._file.to_dict() if self._file else None

        status: Union[Unset, int] = UNSET
        if not isinstance(self._status, Unset):
            status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if complete_with_errors is not UNSET:
            field_dict["completeWithErrors"] = complete_with_errors
        if error_file is not UNSET:
            field_dict["errorFile"] = error_file
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if progress_stats is not UNSET:
            field_dict["progressStats"] = progress_stats
        if transforms is not UNSET:
            field_dict["transforms"] = transforms
        if assay_run_id is not UNSET:
            field_dict["assayRunId"] = assay_run_id
        if automation_file_config is not UNSET:
            field_dict["automationFileConfig"] = automation_file_config
        if file is not UNSET:
            field_dict["file"] = file
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        api_url = get_api_url() if "apiURL" in d else cast(Union[Unset, str], UNSET)

        def get_archive_record() -> Union[Unset, ArchiveRecord]:
            archive_record: Union[Unset, ArchiveRecord] = UNSET
            _archive_record = d.pop("archiveRecord")
            if not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecord.from_dict(_archive_record)

            return archive_record

        archive_record = (
            get_archive_record() if "archiveRecord" in d else cast(Union[Unset, ArchiveRecord], UNSET)
        )

        def get_complete_with_errors() -> Union[Unset, bool]:
            complete_with_errors = d.pop("completeWithErrors")
            return complete_with_errors

        complete_with_errors = (
            get_complete_with_errors() if "completeWithErrors" in d else cast(Union[Unset, bool], UNSET)
        )

        def get_error_file() -> Union[Unset, None, Blob]:
            error_file = None
            _error_file = d.pop("errorFile")
            if _error_file is not None and not isinstance(_error_file, Unset):
                error_file = Blob.from_dict(_error_file)

            return error_file

        error_file = get_error_file() if "errorFile" in d else cast(Union[Unset, None, Blob], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_progress_stats() -> Union[Unset, AutomationProgressStats]:
            progress_stats: Union[Unset, AutomationProgressStats] = UNSET
            _progress_stats = d.pop("progressStats")
            if not isinstance(_progress_stats, Unset):
                progress_stats = AutomationProgressStats.from_dict(_progress_stats)

            return progress_stats

        progress_stats = (
            get_progress_stats()
            if "progressStats" in d
            else cast(Union[Unset, AutomationProgressStats], UNSET)
        )

        def get_transforms() -> Union[Unset, List[LabAutomationTransform]]:
            transforms = []
            _transforms = d.pop("transforms")
            for transforms_item_data in _transforms or []:
                transforms_item = LabAutomationTransform.from_dict(transforms_item_data)

                transforms.append(transforms_item)

            return transforms

        transforms = (
            get_transforms() if "transforms" in d else cast(Union[Unset, List[LabAutomationTransform]], UNSET)
        )

        def get_assay_run_id() -> Union[Unset, str]:
            assay_run_id = d.pop("assayRunId")
            return assay_run_id

        assay_run_id = get_assay_run_id() if "assayRunId" in d else cast(Union[Unset, str], UNSET)

        def get_automation_file_config() -> Union[Unset, AutomationFileAutomationFileConfig]:
            automation_file_config: Union[Unset, AutomationFileAutomationFileConfig] = UNSET
            _automation_file_config = d.pop("automationFileConfig")
            if not isinstance(_automation_file_config, Unset):
                automation_file_config = AutomationFileAutomationFileConfig.from_dict(_automation_file_config)

            return automation_file_config

        automation_file_config = (
            get_automation_file_config()
            if "automationFileConfig" in d
            else cast(Union[Unset, AutomationFileAutomationFileConfig], UNSET)
        )

        def get_file() -> Union[Unset, None, Blob]:
            file = None
            _file = d.pop("file")
            if _file is not None and not isinstance(_file, Unset):
                file = Blob.from_dict(_file)

            return file

        file = get_file() if "file" in d else cast(Union[Unset, None, Blob], UNSET)

        def get_status() -> Union[Unset, AutomationFileStatus]:
            status = None
            _status = d.pop("status")
            if _status is not None and _status is not UNSET:
                try:
                    status = AutomationFileStatus(_status)
                except ValueError:
                    status = AutomationFileStatus.of_unknown(_status)

            return status

        status = get_status() if "status" in d else cast(Union[Unset, AutomationFileStatus], UNSET)

        automation_output_processor = cls(
            api_url=api_url,
            archive_record=archive_record,
            complete_with_errors=complete_with_errors,
            error_file=error_file,
            id=id,
            modified_at=modified_at,
            progress_stats=progress_stats,
            transforms=transforms,
            assay_run_id=assay_run_id,
            automation_file_config=automation_file_config,
            file=file,
            status=status,
        )

        automation_output_processor.additional_properties = d
        return automation_output_processor

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
    def api_url(self) -> str:
        """ The canonical url of the Automation Output Processor in the API. """
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

    @property
    def archive_record(self) -> ArchiveRecord:
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: ArchiveRecord) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET

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

    @property
    def error_file(self) -> Optional[Blob]:
        if isinstance(self._error_file, Unset):
            raise NotPresentError(self, "error_file")
        return self._error_file

    @error_file.setter
    def error_file(self, value: Optional[Blob]) -> None:
        self._error_file = value

    @error_file.deleter
    def error_file(self) -> None:
        self._error_file = UNSET

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def modified_at(self) -> datetime.datetime:
        """ DateTime the Automation Output Processor was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def progress_stats(self) -> AutomationProgressStats:
        """ Processing progress information. """
        if isinstance(self._progress_stats, Unset):
            raise NotPresentError(self, "progress_stats")
        return self._progress_stats

    @progress_stats.setter
    def progress_stats(self, value: AutomationProgressStats) -> None:
        self._progress_stats = value

    @progress_stats.deleter
    def progress_stats(self) -> None:
        self._progress_stats = UNSET

    @property
    def transforms(self) -> List[LabAutomationTransform]:
        if isinstance(self._transforms, Unset):
            raise NotPresentError(self, "transforms")
        return self._transforms

    @transforms.setter
    def transforms(self, value: List[LabAutomationTransform]) -> None:
        self._transforms = value

    @transforms.deleter
    def transforms(self) -> None:
        self._transforms = UNSET

    @property
    def assay_run_id(self) -> str:
        if isinstance(self._assay_run_id, Unset):
            raise NotPresentError(self, "assay_run_id")
        return self._assay_run_id

    @assay_run_id.setter
    def assay_run_id(self, value: str) -> None:
        self._assay_run_id = value

    @assay_run_id.deleter
    def assay_run_id(self) -> None:
        self._assay_run_id = UNSET

    @property
    def automation_file_config(self) -> AutomationFileAutomationFileConfig:
        if isinstance(self._automation_file_config, Unset):
            raise NotPresentError(self, "automation_file_config")
        return self._automation_file_config

    @automation_file_config.setter
    def automation_file_config(self, value: AutomationFileAutomationFileConfig) -> None:
        self._automation_file_config = value

    @automation_file_config.deleter
    def automation_file_config(self) -> None:
        self._automation_file_config = UNSET

    @property
    def file(self) -> Optional[Blob]:
        if isinstance(self._file, Unset):
            raise NotPresentError(self, "file")
        return self._file

    @file.setter
    def file(self, value: Optional[Blob]) -> None:
        self._file = value

    @file.deleter
    def file(self) -> None:
        self._file = UNSET

    @property
    def status(self) -> AutomationFileStatus:
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: AutomationFileStatus) -> None:
        self._status = value

    @status.deleter
    def status(self) -> None:
        self._status = UNSET
