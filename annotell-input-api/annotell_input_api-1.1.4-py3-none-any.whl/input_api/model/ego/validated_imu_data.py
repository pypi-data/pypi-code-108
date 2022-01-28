from typing import Optional, List

from annotell.input_api.model import IMUData
from annotell.input_api.model.calibration.common import BaseSerializer


class ValidatedIMUData(BaseSerializer):
    resource_id: str
    signed_url: Optional[str]
    imu_data: List[IMUData]

    def serialize_imu_data(self):
        return [imud.to_dict() for imud in self.imu_data]


class ValidateIMUDataRequest(BaseSerializer):
    imu_data: List[IMUData]
    internal_id: str
