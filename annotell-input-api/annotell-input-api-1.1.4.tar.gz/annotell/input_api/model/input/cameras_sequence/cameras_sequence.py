from typing import Optional, List, Mapping, Union
from dataclasses import field, dataclass

from annotell.input_api.model.input.cameras_sequence.frame import Frame
from annotell.input_api.model.input.sensor_specification import SensorSpecification


@dataclass
class CamerasSequence:
    external_id: str
    frames: List[Frame]
    sensor_specification: Optional[SensorSpecification] = None
    metadata: Mapping[str, Union[int, float, str, bool]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(
            frames=[frame.to_dict() for frame in self.frames],
            sensorSpecification=self.sensor_specification.to_dict() if isinstance(self.sensor_specification, SensorSpecification) else None,
            externalId=self.external_id,
            metadata=self.metadata
        )
