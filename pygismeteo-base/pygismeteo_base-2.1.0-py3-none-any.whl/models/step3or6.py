# -*- coding: utf-8 -*-
from typing import Iterator as _Iterator
from typing import List as _List
from typing import Optional as _Optional

from pydantic import BaseModel as _BaseModel
from pydantic import Field as _Field


class Precipitation(_BaseModel):
    type_ext: _Optional[int]
    intensity: int
    correction: _Optional[bool]
    amount: _Optional[float]
    duration: int
    type: int


class Pressure(_BaseModel):
    h_pa: int
    mm_hg_atm: int
    in_hg: float


class Humidity(_BaseModel):
    percent: _Optional[int]


class Direction(_BaseModel):
    degree: _Optional[int]
    scale_8: _Optional[int]


class Speed(_BaseModel):
    km_h: int
    m_s: int
    mi_h: int


class Wind(_BaseModel):
    direction: Direction
    speed: Speed


class Cloudiness(_BaseModel):
    type: int
    percent: int


class Date(_BaseModel):
    utc: str = _Field(..., alias="UTC")
    time_zone_offset: int
    local: str
    hr_to_forecast: _Optional[int]
    unix: int


class Radiation(_BaseModel):
    uvb_index: _Optional[int]
    uvb: _Optional[int] = _Field(..., alias="UVB")


class Comfort(_BaseModel):
    c: float = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Water(_BaseModel):
    c: int = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Air(_BaseModel):
    c: float = _Field(..., alias="C")
    f: float = _Field(..., alias="F")


class Temperature(_BaseModel):
    comfort: Comfort
    water: Water
    air: Air


class Description(_BaseModel):
    full: str


class ModelItem(_BaseModel):
    precipitation: Precipitation
    pressure: Pressure
    humidity: Humidity
    icon: str
    gm: int
    wind: Wind
    cloudiness: Cloudiness
    date: Date
    phenomenon: _Optional[int]
    radiation: Radiation
    city: int
    kind: str
    storm: bool
    temperature: Temperature
    description: Description


class Model(_BaseModel):
    __root__: _List[ModelItem]

    def __iter__(self) -> _Iterator[ModelItem]:  # type: ignore
        return iter(self.__root__)

    def __getitem__(self, item: int) -> ModelItem:
        return self.__root__[item]
