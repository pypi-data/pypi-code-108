from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum

from deprecated import deprecated

from annotell.input_api.model.abstract.abstract_models import RequestCall


class CameraType(str, Enum):
    PINHOLE = "pinhole"
    FISHEYE = "fisheye"
    KANNALA = "kannala"


@dataclass
class RotationQuaternion(RequestCall):
    w: float
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict:
        return self.__dict__

    @staticmethod
    def from_json(js: dict):
        return RotationQuaternion(
            w=js["w"],
            x=js["x"],
            y=js["y"],
            z=js["z"],
        )


@dataclass
class Position(RequestCall):
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict:
        return self.__dict__

    @staticmethod
    def from_json(js: dict):
        return Position(
            x=js["x"],
            y=js["y"],
            z=js["z"],
        )


@dataclass
class CameraMatrix(RequestCall):
    fx: float
    fy: float
    cx: float
    cy: float

    def to_dict(self) -> Dict:
        return self.__dict__

    @staticmethod
    def from_json(js: dict):
        return CameraMatrix(
            fx=js["fx"],
            fy=js["fy"],
            cx=js["cx"],
            cy=js["cy"],
        )


@dataclass
class DistortionCoefficients(RequestCall):
    k1: float
    k2: float
    p1: float
    p2: float
    k3: Optional[float] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def validate(self, camera_type: CameraType):
        if camera_type == CameraType.KANNALA:
            assert self.k3 is None
        else:
            assert self.k3 is not None

    @staticmethod
    def from_json(js: dict):
        return DistortionCoefficients(k1=js["k1"], k2=js["k2"], p1=js["p1"], p2=js["p2"], k3=js.get("k3"))


@dataclass
class UndistortionCoefficients(RequestCall):
    l1: float
    l2: float
    l3: float
    l4: float

    def to_dict(self) -> Dict:
        return self.__dict__

    @staticmethod
    def from_json(js: dict):
        if js:
            return UndistortionCoefficients(l1=js["l1"], l2=js["l2"], l3=js["l3"], l4=js["l4"])
        else:
            return None


@deprecated(reason="Will be removed, migrate to typed calibrations", action="once")
@dataclass
class CameraProperty(RequestCall):
    camera_type: CameraType

    def to_dict(self):
        return {"camera_type": self.camera_type}

    def get_camera_type(self) -> CameraType:
        return self.camera_type

    @staticmethod
    def from_json(js: dict):
        return CameraProperty(camera_type=js["camera_type"])


@deprecated(reason="Will be removed, migrate to typed calibrations", action="once")
@dataclass
class LidarCalibration(RequestCall):
    position: Position
    rotation_quaternion: RotationQuaternion

    def to_dict(self) -> Dict:
        return {"position": self.position.to_dict(), "rotation_quaternion": self.rotation_quaternion.to_dict()}

    @staticmethod
    def from_json(js: dict):
        return LidarCalibration(
            position=Position.from_json(js["position"]), rotation_quaternion=RotationQuaternion.from_json(js["rotation_quaternion"])
        )


@deprecated(reason="Will be removed, migrate to typed calibrations", action="once")
@dataclass
class CameraCalibration(RequestCall):
    position: Position
    rotation_quaternion: RotationQuaternion
    camera_matrix: CameraMatrix
    distortion_coefficients: DistortionCoefficients
    camera_properties: CameraProperty
    image_height: int
    image_width: int
    undistortion_coefficients: Optional[UndistortionCoefficients] = None

    def __post_init__(self):
        camera_type = self.camera_properties.get_camera_type()
        self.distortion_coefficients.validate(camera_type=camera_type)
        if camera_type == CameraType.KANNALA:
            assert self.undistortion_coefficients is not None

    def to_dict(self) -> Dict:
        base = {
            "position": self.position.to_dict(),
            "rotation_quaternion": self.rotation_quaternion.to_dict(),
            "camera_matrix": self.camera_matrix.to_dict(),
            "camera_properties": self.camera_properties.to_dict(),
            "distortion_coefficients": self.distortion_coefficients.to_dict(),
            "image_height": self.image_height,
            "image_width": self.image_width
        }
        if self.undistortion_coefficients is not None:
            base["undistortion_coefficients"] = self.undistortion_coefficients.to_dict()

        return base

    @staticmethod
    def from_json(js: dict):
        return CameraCalibration(
            position=Position.from_json(js["position"]),
            rotation_quaternion=RotationQuaternion.from_json(js["rotation_quaternion"]),
            camera_matrix=CameraMatrix.from_json(js["camera_matrix"]),
            distortion_coefficients=DistortionCoefficients.from_json(js["distortion_coefficients"]),
            camera_properties=CameraProperty.from_json(js["camera_properties"]),
            image_height=js["image_height"],
            image_width=js["image_width"],
            undistortion_coefficients=UndistortionCoefficients.from_json(js.get("undistortion_coefficients")),
        )
