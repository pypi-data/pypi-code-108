from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.auto_detect_task_config import AutoDetectTaskConfig
from ..models.data_import_description_config import DataImportDescriptionConfig
from ..models.data_source_details_dto import DataSourceDetailsDTO
from ..models.en_data_source_state import EnDataSourceState
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataSourceResponse")


@attr.s(auto_attribs=True)
class DataSourceResponse:
    """ """

    data_source_id: str
    data_import_description: Union[Unset, None, DataImportDescriptionConfig] = UNSET
    auto_detect_task_configs: Union[Unset, None, List[AutoDetectTaskConfig]] = UNSET
    details: Union[Unset, None, DataSourceDetailsDTO] = UNSET
    created_data_points: Union[Unset, None, List[str]] = UNSET
    state: Union[Unset, EnDataSourceState] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        data_source_id = self.data_source_id
        data_import_description: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.data_import_description, Unset):
            data_import_description = self.data_import_description.to_dict() if self.data_import_description else None

        auto_detect_task_configs: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.auto_detect_task_configs, Unset):
            if self.auto_detect_task_configs is None:
                auto_detect_task_configs = None
            else:
                auto_detect_task_configs = []
                for auto_detect_task_configs_item_data in self.auto_detect_task_configs:
                    auto_detect_task_configs_item = auto_detect_task_configs_item_data.to_dict()

                    auto_detect_task_configs.append(auto_detect_task_configs_item)

        details: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict() if self.details else None

        created_data_points: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.created_data_points, Unset):
            if self.created_data_points is None:
                created_data_points = None
            else:
                created_data_points = self.created_data_points

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dataSourceId": data_source_id,
            }
        )
        if data_import_description is not UNSET:
            field_dict["dataImportDescription"] = data_import_description
        if auto_detect_task_configs is not UNSET:
            field_dict["autoDetectTaskConfigs"] = auto_detect_task_configs
        if details is not UNSET:
            field_dict["details"] = details
        if created_data_points is not UNSET:
            field_dict["createdDataPoints"] = created_data_points
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_source_id = d.pop("dataSourceId")

        _data_import_description = d.pop("dataImportDescription", UNSET)
        data_import_description: Union[Unset, None, DataImportDescriptionConfig]
        if _data_import_description is None:
            data_import_description = None
        elif isinstance(_data_import_description, Unset):
            data_import_description = UNSET
        else:
            data_import_description = DataImportDescriptionConfig.from_dict(_data_import_description)

        auto_detect_task_configs = []
        _auto_detect_task_configs = d.pop("autoDetectTaskConfigs", UNSET)
        for auto_detect_task_configs_item_data in _auto_detect_task_configs or []:
            auto_detect_task_configs_item = AutoDetectTaskConfig.from_dict(auto_detect_task_configs_item_data)

            auto_detect_task_configs.append(auto_detect_task_configs_item)

        _details = d.pop("details", UNSET)
        details: Union[Unset, None, DataSourceDetailsDTO]
        if _details is None:
            details = None
        elif isinstance(_details, Unset):
            details = UNSET
        else:
            details = DataSourceDetailsDTO.from_dict(_details)

        created_data_points = cast(List[str], d.pop("createdDataPoints", UNSET))

        _state = d.pop("state", UNSET)
        state: Union[Unset, EnDataSourceState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = EnDataSourceState(_state)

        data_source_response = cls(
            data_source_id=data_source_id,
            data_import_description=data_import_description,
            auto_detect_task_configs=auto_detect_task_configs,
            details=details,
            created_data_points=created_data_points,
            state=state,
        )

        return data_source_response
