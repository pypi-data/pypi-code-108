from typing import Optional

from annotell.input_api.model.calibration.common import BaseSerializer, BaseCalibration


class CameraMatrix(BaseSerializer):
    fx: float
    fy: float
    cx: float
    cy: float


class DistortionCoefficients(BaseSerializer):
    k1: float
    k2: float
    p1: float
    p2: float
    k3: float


class BaseCameraCalibration(BaseCalibration):
    camera_matrix: CameraMatrix
    image_height: int
    image_width: int
    field_of_view: Optional[float] = None
