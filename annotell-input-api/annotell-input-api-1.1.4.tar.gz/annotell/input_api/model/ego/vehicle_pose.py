from dataclasses import dataclass
from typing import Dict

from annotell.input_api.model.calibration import Position, RotationQuaternion


@dataclass
class EgoVehiclePose:
    """Both `position` and `rotation` are with respect to the local coordinate system (LCS)."""
    position: Position
    rotation: RotationQuaternion

    def to_dict(self) -> Dict:
        return dict(position=self.position.to_dict(), rotation=self.rotation.to_dict())
