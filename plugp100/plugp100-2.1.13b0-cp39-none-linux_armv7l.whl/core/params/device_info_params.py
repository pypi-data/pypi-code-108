import dataclasses
from dataclasses import dataclass
from typing import Optional


# TODO: improve this classes

@dataclass
class DeviceInfoParams:
    def as_dict(self):  # custom as_dict that remove None fields
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass
class SwitchParams(DeviceInfoParams):
    device_on: Optional[bool]


@dataclass
class LightParams(SwitchParams):
    brightness: Optional[int]
    color_temp: Optional[int]
    saturation: Optional[int]
    hue: Optional[int]

    def __init__(self,
                 brightness: Optional[int] = None,
                 color_temperature: Optional[int] = None,
                 saturation: Optional[int] = None,
                 hue: Optional[int] = None):
        self.device_on = None
        self.brightness = brightness
        self.color_temp = color_temperature
        self.saturation = saturation
        self.hue = hue
