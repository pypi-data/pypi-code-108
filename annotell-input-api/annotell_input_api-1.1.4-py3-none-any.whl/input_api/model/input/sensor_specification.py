from typing import Optional, List, Dict, Mapping
from dataclasses import dataclass

from annotell.input_api.util import filter_none


@dataclass
class CameraSettings:
    width: int
    height: int

    def to_dict(self):
        return filter_none({"width": self.width, "height": self.height})


@dataclass
class SensorSpecification:
    sensor_to_pretty_name: Optional[Dict[str, str]] = None
    sensor_order: Optional[List[str]] = None

    def to_dict(self):
        return filter_none({
            "sensorToPrettyName": self.sensor_to_pretty_name,
            "sensorOrder": self.sensor_order,
        })
