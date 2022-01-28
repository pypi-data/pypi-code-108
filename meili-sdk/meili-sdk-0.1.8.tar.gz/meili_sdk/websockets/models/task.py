import typing as t

from meili_sdk.models.base import BaseModel

__all__ = (
    "IndoorPoint",
    "OutdoorPoint",
    "Task",
)


class IndoorPoint(BaseModel):
    uuid: str
    x: int
    y: int
    rotation: float
    metric: t.Dict[str, int]


class OutdoorPoint(BaseModel):
    uuid: str
    location_data: t.List[float]


class Task(BaseModel):
    uuid: str
    number: str
    location: t.Union[IndoorPoint, OutdoorPoint]

    def __init__(self, location: dict, **kwargs):
        if "location_data" in location:
            kwargs["location"] = OutdoorPoint(**location)
        else:
            kwargs["location"] = IndoorPoint(**location)
        super().__init__(**kwargs)
