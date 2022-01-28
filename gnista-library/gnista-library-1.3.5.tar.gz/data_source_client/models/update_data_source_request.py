from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.auto_detect_task_config import AutoDetectTaskConfig
from ..models.data_import_description_config import DataImportDescriptionConfig
from ..models.data_source_details_request import DataSourceDetailsRequest
from ..models.en_data_source_state import EnDataSourceState
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDataSourceRequest")


@attr.s(auto_attribs=True)
class UpdateDataSourceRequest:
    """ """

    data_import_description: Union[Unset, None, DataImportDescriptionConfig] = UNSET
    details: Union[Unset, None, DataSourceDetailsRequest] = UNSET
    auto_detect_task_configs: Union[Unset, None, List[AutoDetectTaskConfig]] = UNSET
    state: Union[Unset, None, EnDataSourceState] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        data_import_description: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.data_import_description, Unset):
            data_import_description = self.data_import_description.to_dict() if self.data_import_description else None

        details: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict() if self.details else None

        auto_detect_task_configs: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.auto_detect_task_configs, Unset):
            if self.auto_detect_task_configs is None:
                auto_detect_task_configs = None
            else:
                auto_detect_task_configs = []
                for auto_detect_task_configs_item_data in self.auto_detect_task_configs:
                    auto_detect_task_configs_item = auto_detect_task_configs_item_data.to_dict()

                    auto_detect_task_configs.append(auto_detect_task_configs_item)

        state: Union[Unset, None, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value if self.state else None

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if data_import_description is not UNSET:
            field_dict["dataImportDescription"] = data_import_description
        if details is not UNSET:
            field_dict["details"] = details
        if auto_detect_task_configs is not UNSET:
            field_dict["autoDetectTaskConfigs"] = auto_detect_task_configs
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _data_import_description = d.pop("dataImportDescription", UNSET)
        data_import_description: Union[Unset, None, DataImportDescriptionConfig]
        if _data_import_description is None:
            data_import_description = None
        elif isinstance(_data_import_description, Unset):
            data_import_description = UNSET
        else:
            data_import_description = DataImportDescriptionConfig.from_dict(_data_import_description)

        _details = d.pop("details", UNSET)
        details: Union[Unset, None, DataSourceDetailsRequest]
        if _details is None:
            details = None
        elif isinstance(_details, Unset):
            details = UNSET
        else:
            details = DataSourceDetailsRequest.from_dict(_details)

        auto_detect_task_configs = []
        _auto_detect_task_configs = d.pop("autoDetectTaskConfigs", UNSET)
        for auto_detect_task_configs_item_data in _auto_detect_task_configs or []:
            auto_detect_task_configs_item = AutoDetectTaskConfig.from_dict(auto_detect_task_configs_item_data)

            auto_detect_task_configs.append(auto_detect_task_configs_item)

        _state = d.pop("state", UNSET)
        state: Union[Unset, None, EnDataSourceState]
        if _state is None:
            state = None
        elif isinstance(_state, Unset):
            state = UNSET
        else:
            state = EnDataSourceState(_state)

        update_data_source_request = cls(
            data_import_description=data_import_description,
            details=details,
            auto_detect_task_configs=auto_detect_task_configs,
            state=state,
        )

        return update_data_source_request
