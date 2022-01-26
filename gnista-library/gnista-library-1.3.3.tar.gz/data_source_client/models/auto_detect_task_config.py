import datetime
from typing import Any, Dict, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.data_import_task_config import DataImportTaskConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutoDetectTaskConfig")


@attr.s(auto_attribs=True)
class AutoDetectTaskConfig:
    """ """

    date_time_header: Union[Unset, None, str] = UNSET
    value_header: Union[Unset, None, str] = UNSET
    date_time_raw: Union[Unset, None, str] = UNSET
    date_time_parsed: Union[Unset, None, datetime.datetime] = UNSET
    value_raw: Union[Unset, None, str] = UNSET
    value_parsed: Union[Unset, None, float] = UNSET
    import_task_config: Union[Unset, None, DataImportTaskConfig] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        date_time_header = self.date_time_header
        value_header = self.value_header
        date_time_raw = self.date_time_raw
        date_time_parsed: Union[Unset, None, str] = UNSET
        if not isinstance(self.date_time_parsed, Unset):
            date_time_parsed = self.date_time_parsed.isoformat() if self.date_time_parsed else None

        value_raw = self.value_raw
        value_parsed = self.value_parsed
        import_task_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.import_task_config, Unset):
            import_task_config = self.import_task_config.to_dict() if self.import_task_config else None

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if date_time_header is not UNSET:
            field_dict["dateTimeHeader"] = date_time_header
        if value_header is not UNSET:
            field_dict["valueHeader"] = value_header
        if date_time_raw is not UNSET:
            field_dict["dateTimeRaw"] = date_time_raw
        if date_time_parsed is not UNSET:
            field_dict["dateTimeParsed"] = date_time_parsed
        if value_raw is not UNSET:
            field_dict["valueRaw"] = value_raw
        if value_parsed is not UNSET:
            field_dict["valueParsed"] = value_parsed
        if import_task_config is not UNSET:
            field_dict["importTaskConfig"] = import_task_config

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        date_time_header = d.pop("dateTimeHeader", UNSET)

        value_header = d.pop("valueHeader", UNSET)

        date_time_raw = d.pop("dateTimeRaw", UNSET)

        _date_time_parsed = d.pop("dateTimeParsed", UNSET)
        date_time_parsed: Union[Unset, None, datetime.datetime]
        if _date_time_parsed is None:
            date_time_parsed = None
        elif isinstance(_date_time_parsed, Unset):
            date_time_parsed = UNSET
        else:
            date_time_parsed = isoparse(_date_time_parsed)

        value_raw = d.pop("valueRaw", UNSET)

        value_parsed = d.pop("valueParsed", UNSET)

        _import_task_config = d.pop("importTaskConfig", UNSET)
        import_task_config: Union[Unset, None, DataImportTaskConfig]
        if _import_task_config is None:
            import_task_config = None
        elif isinstance(_import_task_config, Unset):
            import_task_config = UNSET
        else:
            import_task_config = DataImportTaskConfig.from_dict(_import_task_config)

        auto_detect_task_config = cls(
            date_time_header=date_time_header,
            value_header=value_header,
            date_time_raw=date_time_raw,
            date_time_parsed=date_time_parsed,
            value_raw=value_raw,
            value_parsed=value_parsed,
            import_task_config=import_task_config,
        )

        return auto_detect_task_config
