from annotell.input_api.model.calibration.camera.common import BaseCameraCalibration, DistortionCoefficients
from annotell.input_api.model.calibration.common import CalibrationType


class PinholeCalibration(BaseCameraCalibration):
    calibration_type = CalibrationType.PINHOLE.value
    distortion_coefficients: DistortionCoefficients
