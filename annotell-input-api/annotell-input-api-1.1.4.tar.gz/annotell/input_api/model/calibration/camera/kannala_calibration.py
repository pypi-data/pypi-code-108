from annotell.input_api.model.calibration.camera.common import BaseCameraCalibration
from annotell.input_api.model.calibration.common import CalibrationType
from annotell.input_api.model.base_serializer import BaseSerializer


class KannalaDistortionCoefficients(BaseSerializer):
    k1: float
    k2: float
    p1: float
    p2: float


class UndistortionCoefficients(BaseSerializer):
    l1: float
    l2: float
    l3: float
    l4: float


class KannalaCalibration(BaseCameraCalibration):
    calibration_type = CalibrationType.KANNALA.value
    distortion_coefficients: KannalaDistortionCoefficients
    undistortion_coefficients: UndistortionCoefficients
