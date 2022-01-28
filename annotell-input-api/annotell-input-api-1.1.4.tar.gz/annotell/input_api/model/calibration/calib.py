from datetime import datetime
from typing import Dict, Mapping, Optional, Union
from dataclasses import dataclass

from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt
from annotell.input_api.model.calibration import sensors as CM
from annotell.input_api.model.calibration.common import BaseCalibration, CalibrationType
from annotell.input_api.model.calibration.lidar.lidar_calibration import LidarCalibration
from annotell.input_api.model.calibration.camera.kannala_calibration import KannalaCalibration
from annotell.input_api.model.calibration.camera.fisheye_calibration import FisheyeCalibration
from annotell.input_api.model.calibration.camera.pinhole_calibration import PinholeCalibration


@dataclass
class SensorCalibration:
    external_id: str
    calibration: Dict[str, Union[BaseCalibration, CM.CameraCalibration]]

    def to_dict(self):
        return {'externalId': self.external_id, 'calibration': {k: v.to_dict(by_alias=False) for (k, v) in self.calibration.items()}}


@dataclass
class SensorCalibrationEntry(Response):
    id: str
    external_id: str
    created: datetime
    calibration: Optional[Mapping[str, Union[BaseCalibration, CM.CameraCalibration]]]

    @classmethod
    def from_json(cls, js: dict):
        calibrations = js.get("calibration", {})

        calibration = {}
        for sensor, calib in calibrations.items():
            calibration[sensor] = cls._parse_calibration(calib)
        return SensorCalibrationEntry(id=js["id"], external_id=js["externalId"], created=ts_to_dt(js["created"]), calibration=calibration)

    @staticmethod
    def _parse_calibration(calibration: Dict) -> Union[BaseCalibration, CM.CameraCalibration]:

        calibration_type = calibration.get("calibration_type")
        if calibration_type is None:
            if calibration.get("camera_matrix") is None:
                return LidarCalibration.parse_obj(calibration)
            return CM.CameraCalibration.from_json(calibration)

        if calibration_type == CalibrationType.PINHOLE:
            return PinholeCalibration.parse_obj(calibration)

        if calibration_type == CalibrationType.KANNALA:
            return KannalaCalibration.parse_obj(calibration)

        if calibration_type == CalibrationType.FISHEYE:
            return FisheyeCalibration.parse_obj(calibration)

        if calibration_type == CalibrationType.LIDAR:
            return LidarCalibration.parse_obj(calibration)

        raise TypeError(f"Unable to parse calibration type: {calibration_type}")
