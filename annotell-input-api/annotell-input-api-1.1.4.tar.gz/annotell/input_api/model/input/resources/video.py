from annotell.input_api.model.input.resources.resource import Resource
from typing import Optional
from abc import ABC
from dataclasses import dataclass
from annotell.input_api.util import filter_none

camera_sensor_default = "CAM"


@dataclass
class VideoTS(ABC):
    video_timestamp: int


@dataclass
class VideoFrame(Resource, VideoTS):
    filename: str
    resource_id: Optional[str] = None
    sensor_name: str = camera_sensor_default
    video_timestamp: int

    def to_dict(self) -> dict:
        return filter_none(
            {
                "filename": self.filename,
                "videoTimestamp": self.video_timestamp,
                "sensorName": self.sensor_name,
                "resourceId": self.resolve_resource_id()
            }
        )
