from dataclasses import field, dataclass
from typing import Union, Mapping, List

from annotell.input_api.model import IMUData
from annotell.input_api.model.input.lidars_and_cameras.frame import Frame


@dataclass
class Lidars:
    external_id: str
    frame: Frame
    metadata: Mapping[str, Union[int, float, str, bool]] = field(default_factory=dict)
    imu_data: List[IMUData] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dict(frame=self.frame.to_dict(), externalId=self.external_id, metadata=self.metadata)
