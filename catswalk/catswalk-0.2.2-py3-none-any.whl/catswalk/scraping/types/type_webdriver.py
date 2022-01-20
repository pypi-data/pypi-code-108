from enum import Enum
from dataclasses import dataclass
from typing import List, Mapping

class EXECUTION_ENV(Enum):
    LOCAL = "local"
    LOCAL_HEADLESS = "local_headless"
    AWS_LAMBDA = "aws_lambda"

    @classmethod
    def str_to_enum(cls, s):
        if s == "local":
            return EXECUTION_ENV.LOCAL
        elif s == "local_headless":
            return EXECUTION_ENV.LOCAL_HEADLESS
        elif s == "aws_lambda":
            return EXECUTION_ENV.AWS_LAMBDA
        else:
            raise Exception(f"EXECUTION_ENV type not found: {s}")


@dataclass
class DeviceType:
    """[summary]
    """
    mode: str
    agent: str

class DEVICE_MODE(Enum):
    DESKTOP = "Desktop"
    MOBILE = "Mobile"

class DEVICE(Enum):
    DESKTOP_GENERAL = DeviceType(mode=DEVICE_MODE.DESKTOP, agent="desktop_general")
    MOBILE_GALAXY_S5 = DeviceType(mode=DEVICE_MODE.MOBILE, agent="Galaxy_S5")

    @classmethod
    def str_to_enum(cls, s):
        if s == "desktop_general":
            return DEVICE.DESKTOP_GENERAL
        elif s == "Galaxy_S5":
            return DEVICE.MOBILE_GALAXY_S5
        else:
            raise Exception(f"DEVICE type not found: {s}")
    