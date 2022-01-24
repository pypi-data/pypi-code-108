from pydantic import BaseModel
from typing import Tuple


class PolygonFeatures(BaseModel):
    path_length: float
    area: float
    centroid: Tuple[float, float]
    bbox: Tuple[float, float, float, float]
    moments_hu: Tuple[float, float, float, float, float, float, float]

    @classmethod
    def calculate_features(cls, annotation: 'PointsAnnotation'):

        hu_moments = tuple(annotation.hu_moments.flatten())
        return cls(
            path_length=annotation.path_length,
            area=annotation.area,
            bbox=tuple(annotation.bbox),
            centroid=annotation.centroid,
            moments_hu=hu_moments
        )
