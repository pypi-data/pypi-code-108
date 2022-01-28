from enum import Enum

from annotell.input_api.model.base_serializer import BaseSerializer


class CalibrationType(str, Enum):
    PINHOLE = "pinhole"
    FISHEYE = "fisheye"
    KANNALA = "kannala"
    LIDAR = "lidar"


class RotationQuaternion(BaseSerializer):
    w: float
    x: float
    y: float
    z: float


class Position(BaseSerializer):
    x: float
    y: float
    z: float


class BaseCalibration(BaseSerializer):
    position: Position
    rotation_quaternion: RotationQuaternion
