from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.gnista_unit_response import GnistaUnitResponse
from ..types import UNSET, Unset

T = TypeVar("T", bound="InfluxDbImportTaskConfig")


@attr.s(auto_attribs=True)
class InfluxDbImportTaskConfig:
    """ """

    discriminator: str
    name: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET
    connection_string: Union[Unset, None, str] = UNSET
    agent_type: Union[Unset, None, str] = UNSET
    database: Union[Unset, None, str] = UNSET
    measurement: Union[Unset, None, str] = UNSET
    field_name: Union[Unset, None, str] = UNSET
    data_point_id: Union[Unset, None, str] = UNSET
    unit: Union[Unset, None, str] = UNSET
    gnista_unit: Union[Unset, None, GnistaUnitResponse] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        name = self.name
        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags

        connection_string = self.connection_string
        agent_type = self.agent_type
        database = self.database
        measurement = self.measurement
        field_name = self.field_name
        data_point_id = self.data_point_id
        unit = self.unit
        gnista_unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.gnista_unit, Unset):
            gnista_unit = self.gnista_unit.to_dict() if self.gnista_unit else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if tags is not UNSET:
            field_dict["tags"] = tags
        if connection_string is not UNSET:
            field_dict["connectionString"] = connection_string
        if agent_type is not UNSET:
            field_dict["agentType"] = agent_type
        if database is not UNSET:
            field_dict["database"] = database
        if measurement is not UNSET:
            field_dict["measurement"] = measurement
        if field_name is not UNSET:
            field_dict["fieldName"] = field_name
        if data_point_id is not UNSET:
            field_dict["dataPointId"] = data_point_id
        if unit is not UNSET:
            field_dict["unit"] = unit
        if gnista_unit is not UNSET:
            field_dict["gnistaUnit"] = gnista_unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        name = d.pop("name", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        connection_string = d.pop("connectionString", UNSET)

        agent_type = d.pop("agentType", UNSET)

        database = d.pop("database", UNSET)

        measurement = d.pop("measurement", UNSET)

        field_name = d.pop("fieldName", UNSET)

        data_point_id = d.pop("dataPointId", UNSET)

        unit = d.pop("unit", UNSET)

        _gnista_unit = d.pop("gnistaUnit", UNSET)
        gnista_unit: Union[Unset, None, GnistaUnitResponse]
        if _gnista_unit is None:
            gnista_unit = None
        elif isinstance(_gnista_unit, Unset):
            gnista_unit = UNSET
        else:
            gnista_unit = GnistaUnitResponse.from_dict(_gnista_unit)

        influx_db_import_task_config = cls(
            discriminator=discriminator,
            name=name,
            tags=tags,
            connection_string=connection_string,
            agent_type=agent_type,
            database=database,
            measurement=measurement,
            field_name=field_name,
            data_point_id=data_point_id,
            unit=unit,
            gnista_unit=gnista_unit,
        )

        influx_db_import_task_config.additional_properties = d
        return influx_db_import_task_config

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
