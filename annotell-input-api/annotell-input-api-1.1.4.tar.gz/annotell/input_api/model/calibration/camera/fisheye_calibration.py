from annotell.input_api.model.calibration.camera.common import BaseCameraCalibration, DistortionCoefficients
from annotell.input_api.model.calibration.common import CalibrationType


class FisheyeCalibration(BaseCameraCalibration):
    calibration_type = CalibrationType.FISHEYE.value
    distortion_coefficients: DistortionCoefficients
    xi: float
