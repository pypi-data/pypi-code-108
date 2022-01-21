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
    MOBILE_GALAXY_S5 = DeviceType(mode=DEVICE_MODE.MOBILE, agent="Galaxy S5")
    MOBILE_iPhone_X = DeviceType(mode=DEVICE_MODE.MOBILE, agent="iPhone X")
    MOBILE_iPad_Pro = DeviceType(mode=DEVICE_MODE.MOBILE, agent="iPad Pro")
    MOBILE_Kindle_Fire_HDX = DeviceType(mode=DEVICE_MODE.MOBILE, agent="Kindle Fire HDX")
    MOBILE_Nexus_6P = DeviceType(mode=DEVICE_MODE.MOBILE, agent="Nexus 6P")
    MOBILE_iPhone_8_Plus = DeviceType(mode=DEVICE_MODE.MOBILE, agent="iPhone 6/7/8 Plus")
    # Galaxy S5

    @classmethod
    def str_to_enum(cls, s):
        if s == "desktop_general":
            return DEVICE.DESKTOP_GENERAL
        elif s == "Galaxy_S5":
            return DEVICE.MOBILE_GALAXY_S5
        elif s == "iPhone_X":
            return DEVICE.MOBILE_iPhone_X
        elif s == "iPad_Pro":
            return DEVICE.MOBILE_iPad_Pro
        elif s == "Kindle_Fire_HDX":
            return DEVICE.MOBILE_Kindle_Fire_HDX
        elif s == "Nexus_6P":
            return DEVICE.MOBILE_Nexus_6P
        elif s == "iPhone_8_Plus":
            return DEVICE.MOBILE_iPhone_8_Plus
        else:
            raise Exception(f"DEVICE type not found: {s}")
    