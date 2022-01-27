import json
from typing import Dict, List, Union

PROJECT_FUNCTION_MAP = "ProjectFunctionMap"
PROJECT_PROPERTIES = "Projectproperties"


class Config:
    def __init__(self, config: Dict, function_name: str, repoconfig: Dict):
        self.function_name = function_name
        self.repoconfig = repoconfig

        model_settings = config["modelSettings"]
        model_description = config["modelDescription"]

        self.schedule: Schedule = Schedule(config.get("schedule", {}))

        self.front_end_name: str = model_description["frontEndName"]
        self.description: str = model_description["description"]
        self.long_description: str = model_description["longDescription"]

        self.deploy: List[str] = self._retrieve_deployment_information()
        self.model_version: str = model_settings["modelVersion"]
        self.send_alerts: bool = bool(model_settings["sendAlerts"])
        self.display_in_front_end: bool = bool(model_settings["displayInFrontEnd"])
        self.backfill: bool = bool(model_settings["backfill"])
        self.dependencies: List = model_settings.get("dependencies", [])
        self.air_infrastructure: bool = bool(config.get("airInfra"))
        self.load_balancer: bool = bool(config.get("loadBalancer"))
        self.secret_names: List[str] = model_settings.get("secrets")
        self.fields: Union[Fields, None] = Fields(config.get("fields", {})) if config.get("fields") else None
        self.visualization: Union[Visualization, None] = (
            Visualization(config.get("visualization", {})) if config.get("visualization") else None
        )

    def _retrieve_deployment_information(self) -> List[str]:
        project_function_map = self.repoconfig.get(PROJECT_FUNCTION_MAP, {}).get(self.function_name, [])
        projects = list(self.repoconfig[PROJECT_PROPERTIES].keys())
        return project_function_map or projects

    def to_dict(self):
        convert = {
            "description": self.description,
            "modelVersion": self.model_version,
            "frontEndName": self.front_end_name,
            "sendAlerts": self.send_alerts,
            "longDescription": self.long_description,
            "displayInFrontEnd": self.display_in_front_end,
            "backfill": self.backfill,
        }
        if self.schedule.to_dict():
            convert.update({"schedule": self.schedule.to_dict()})
        if self.dependencies:
            convert.update({"dependencies": self.dependencies})
        if self.air_infrastructure:
            convert.update({"airInfra": self.air_infrastructure})
        if self.load_balancer:
            convert.update({"load_balancer": self.load_balancer})
        if self.fields:
            convert.update({"fields": self.fields.to_dict()})
        if self.visualization:
            convert.update({"visualization": self.visualization.to_dict()})
        return convert

    def __repr__(self):
        return json.dumps(self.to_dict())


class Schedule:
    def __init__(self, schedule: dict):
        self.cron_expression: Union[str, None] = schedule.get("cronExpression")

    def to_dict(self):
        convert = {}
        if self.cron_expression:
            convert.update({"cronExpression": self.cron_expression})
        return convert


class Field:
    def __init__(
        self,
        id: str,
        name: Union[str, None] = None,
        description: Union[str, None] = None,
        type: Union[str, None] = None,
        multiple: Union[bool, None] = None,
        units: Union[List[str], None] = None,
    ):
        self.id: str = id
        self.name: Union[str, None] = name
        self.description: Union[str, None] = description
        self.type: Union[str, None] = type
        self.multiple: Union[bool, None] = multiple
        self.units: Union[List[str], None] = units

    def to_dict(self):
        convert = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
        }
        if self.multiple is not None:
            convert.update({"multiple": self.multiple})

        if self.units:
            convert.update({"units": self.units})

        return convert

    def __repr__(self):
        return f"{self.id}, {self.name}, {self.description}, {self.multiple}"


class Fields:
    def __init__(self, fields: Dict):
        self.fields = fields
        self.field_ids: List = list(self.fields.keys())
        self._get_fields: List = []

    @property
    def get_fields(self):
        if self._get_fields:
            return self._get_fields

        local_fields = []
        for field_id in self.field_ids:
            field1 = Field(id=field_id, **self.fields[field_id])
            local_fields.append(field1)
        self._get_fields = local_fields
        return self._get_fields

    def to_dict(self):
        return [field.to_dict() for field in self.get_fields]

    def __repr__(self):
        return " - ".join(self.field_ids)


class Visualization:
    def __init__(self, visualization: Dict):
        self.visualization = visualization
        self.time_series = self.visualization.get("timeSeries", {})
        self.time_series_field_ids = self.time_series.get("fields", [])
        self.thresholds = self.visualization.get("thresholds", {})
        self.thresholds_field_ids = self.thresholds.get("fields", [])
        self.grouping = self.visualization.get("grouping")

    def to_dict(self):
        convert = {
            "timeSeries": {"fields": self.time_series_field_ids},
            "thresholds": {"fields": self.thresholds_field_ids},
        }
        if self.grouping:
            convert["grouping"] = self.grouping
        return convert

    def __repr__(self):
        return self.to_dict()
