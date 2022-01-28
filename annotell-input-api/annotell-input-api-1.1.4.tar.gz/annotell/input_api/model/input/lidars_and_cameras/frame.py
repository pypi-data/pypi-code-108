from typing import List
from dataclasses import dataclass, field
from annotell.input_api.model.input.resources.image import Image
from annotell.input_api.model.input.resources.point_cloud import PointCloud


@dataclass
class Frame:
    point_clouds: List[PointCloud] = field(default_factory=list)
    images: List[Image] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dict(
            pointClouds=[pc.to_dict() for pc in self.point_clouds] if self.point_clouds else None,
            images=[image.to_dict() for image in self.images] if self.images else None
        )
