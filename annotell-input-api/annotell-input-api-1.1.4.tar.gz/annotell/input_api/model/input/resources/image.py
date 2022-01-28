from dataclasses import dataclass
from typing import Optional

from annotell.input_api.util import filter_none
from annotell.input_api.model.input.resources.resource import Resource

camera_sensor_default = "CAM"


@dataclass
class Image(Resource):
    filename: str
    resource_id: Optional[str] = None
    sensor_name: str = camera_sensor_default

    def to_dict(self) -> dict:
        return filter_none({"filename": self.filename, "resourceId": self.resolve_resource_id(), "sensorName": self.sensor_name})
