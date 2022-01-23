# -*- coding: utf-8 -*-
from typing import Iterator as _Iterator
from typing import List as _List
from typing import Optional as _Optional

from pydantic import BaseModel as _BaseModel
from pydantic import Field as _Field


class Precipitation(_BaseModel):
    type_ext: _Optional[int]
    intensity: int
    amount: float
    type: int


class HPa(_BaseModel):
    max: int
    min: int


class MmHgAtm(_BaseModel):
    max: int
    min: int


class InHg(_BaseModel):
    max: float
    min: float


class Pressure(_BaseModel):
    h_pa: HPa
    mm_hg_atm: MmHgAtm
    in_hg: InHg


class Percent(_BaseModel):
    max: int
    min: int
    avg: int


class Humidity(_BaseModel):
    percent: Percent


class Description(_BaseModel):
    full: str


class Cloudiness(_BaseModel):
    type: int
    percent: int


class Date(_BaseModel):
    utc: str = _Field(..., alias="UTC")
    local: str
    time_zone_offset: int
    unix: int


class Radiation(_BaseModel):
    max: _Optional[int]
    max_index: _Optional[int]


class Max(_BaseModel):
    c: float = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Min(_BaseModel):
    c: float = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Comfort(_BaseModel):
    max: Max
    min: Min


class Max1(_BaseModel):
    c: _Optional[int] = _Field(..., alias="C")
    f: _Optional[float] = _Field(..., alias="F")


class Min1(_BaseModel):
    c: int = _Field(..., alias="C")
    f: int = _Field(..., alias="F")


class Water(_BaseModel):
    max: Max1
    min: Min1


class Max2(_BaseModel):
    c: float = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Min2(_BaseModel):
    c: float = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Avg(_BaseModel):
    c: float = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Air(_BaseModel):
    max: Max2
    min: Min2
    avg: Avg


class Temperature(_BaseModel):
    comfort: Comfort
    water: Water
    air: Air


class Max3(_BaseModel):
    km_h: int
    m_s: int
    mi_h: int


class Min3(_BaseModel):
    km_h: int
    m_s: int
    mi_h: int


class Avg1(_BaseModel):
    km_h: _Optional[int]
    m_s: _Optional[int]
    mi_h: _Optional[int]


class Speed(_BaseModel):
    max: Max3
    min: Min3
    avg: Avg1


class Max4(_BaseModel):
    degree: _Optional[int]
    scale_8: _Optional[int]


class Min4(_BaseModel):
    degree: _Optional[int]
    scale_8: _Optional[int]


class Avg2(_BaseModel):
    degree: _Optional[int]
    scale_8: _Optional[int]


class Direction(_BaseModel):
    max: Max4
    min: Min4
    avg: Avg2


class Wind(_BaseModel):
    speed: Speed
    direction: Direction


class ModelItem(_BaseModel):
    precipitation: Precipitation
    pressure: Pressure
    humidity: Humidity
    gm: int
    description: Description
    cloudiness: Cloudiness
    date: Date
    phenomenon: _Optional[int]
    radiation: Radiation
    city: int
    kind: _Optional[str]
    storm: bool
    temperature: Temperature
    wind: Wind
    icon: str


class Model(_BaseModel):
    __root__: _List[ModelItem]

    def __iter__(self) -> _Iterator[ModelItem]:  # type: ignore
        return iter(self.__root__)

    def __getitem__(self, item: int) -> ModelItem:
        return self.__root__[item]
