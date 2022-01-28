from dataclasses import field, dataclass
from typing import Union, Mapping, Optional, List

from annotell.input_api.model.ego.imu_data import IMUData
from annotell.input_api.model.input.lidars_and_cameras.frame import Frame
from annotell.input_api.model.input.sensor_specification import SensorSpecification


@dataclass
class LidarsAndCameras:
    external_id: str
    frame: Frame
    calibration_id: str
    sensor_specification: Optional[SensorSpecification] = None
    metadata: Mapping[str, Union[int, float, str, bool]] = field(default_factory=dict)
    imu_data: List[IMUData] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dict(
            frame=self.frame.to_dict(),
            sensorSpecification=self.sensor_specification.to_dict() if isinstance(self.sensor_specification, SensorSpecification) else None,
            externalId=self.external_id,
            calibrationId=self.calibration_id,
            metadata=self.metadata
        )
