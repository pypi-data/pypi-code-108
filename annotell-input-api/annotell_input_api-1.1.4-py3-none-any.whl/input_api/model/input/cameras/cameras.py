from dataclasses import dataclass, field
from typing import Mapping, Union
from typing import Optional

from annotell.input_api.model.input.cameras.frame import Frame
from annotell.input_api.model.input.sensor_specification import SensorSpecification


@dataclass
class Cameras:
    external_id: str
    frame: Frame
    sensor_specification: Optional[SensorSpecification] = None
    metadata: Mapping[str, Union[int, float, str, bool]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(
            frame=self.frame.to_dict(),
            sensorSpecification=self.sensor_specification.to_dict() if isinstance(self.sensor_specification, SensorSpecification) else None,
            externalId=self.external_id,
            metadata=self.metadata
        )
