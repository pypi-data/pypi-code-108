from dataclasses import dataclass, field
from typing import List, Mapping, Union, Optional

from annotell.input_api.model import UnixTimestampNs
from annotell.input_api.model.ego import EgoVehiclePose
from annotell.input_api.model.input.abstract.sequence_frame import SequenceFrame
from annotell.input_api.model.input.resources import PointCloud, Image, VideoFrame


@dataclass
class Frame(SequenceFrame):
    point_clouds: List[PointCloud] = field(default_factory=list)
    ego_vehicle_pose: Optional[EgoVehiclePose] = None
    metadata: Mapping[str, Union[int, float, str, bool]] = field(default_factory=dict)
    unix_timestamp: Optional[UnixTimestampNs] = None

    def to_dict(self) -> dict:
        return dict(
            frameId=self.frame_id,
            relativeTimestamp=self.relative_timestamp,
            pointClouds=[pc.to_dict() for pc in self.point_clouds] if self.point_clouds else None,
            egoVehiclePose=self.ego_vehicle_pose.to_dict() if self.ego_vehicle_pose else None,
            metadata=self.metadata,
            unixTimestamp=self.unix_timestamp
        )
