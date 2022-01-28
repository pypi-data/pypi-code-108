from annotell.input_api.model.calibration.common import BaseCalibration, CalibrationType


class LidarCalibration(BaseCalibration):
    calibration_type = CalibrationType.LIDAR
