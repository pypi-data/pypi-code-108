from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.data_import_task_config import DataImportTaskConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataImportRequest")


@attr.s(auto_attribs=True)
class DataImportRequest:
    """ """

    data_source_id: str
    task_config: Union[Unset, None, DataImportTaskConfig] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        data_source_id = self.data_source_id
        task_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.task_config, Unset):
            task_config = self.task_config.to_dict() if self.task_config else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dataSourceId": data_source_id,
            }
        )
        if task_config is not UNSET:
            field_dict["taskConfig"] = task_config

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_source_id = d.pop("dataSourceId")

        _task_config = d.pop("taskConfig", UNSET)
        task_config: Union[Unset, None, DataImportTaskConfig]
        if _task_config is None:
            task_config = None
        elif isinstance(_task_config, Unset):
            task_config = UNSET
        else:
            task_config = DataImportTaskConfig.from_dict(_task_config)

        data_import_request = cls(
            data_source_id=data_source_id,
            task_config=task_config,
        )

        return data_import_request
