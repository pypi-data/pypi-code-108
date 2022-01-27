from numpy import float32
from dataclasses import dataclass, field
from typing import List, Union
from .utils import clamp

@dataclass
class Vector2:
    x: int
    y: int
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

@dataclass
class HitCircleOsu:
    position: Vector2
    start_time: int
    end_time: int

@dataclass
class SliderOsu:
    position: Vector2
    start_time: int
    end_time: int
    repeat_count: int
    length: float

@dataclass
class SpinnerOsu:
    start_time: int
    end_time: int

HitObject = Union[HitCircleOsu, SliderOsu, SpinnerOsu]

@dataclass
class ControlPoint:
    offset: float
    beat_length: float
    timing_change: bool

    def bpm_multiplier(self):
        if self.beat_length >= 0:
            return 1
        return clamp(float32(-self.beat_length), 10, 1000) / float32(100)

@dataclass
class Beatmap:
    # Metadata
    title: str = ""
    title_unicode: str = None
    artist: str = ""
    artist_unicode: str = None
    creator: str = ""
    version: str = ""
    source: str = ""
    tags: str = ""
    beatmap_id: int = 0
    beatmapset_id: int = -1

    # Difficulty
    hp: float32 = float32(5)
    cs: float32 = float32(5)
    od: float32 = float32(5)
    ar: float32 = float32(5)
    rot_ratio: float32 = float32(5)
    slider_multiplier: float = float(1.4)
    slider_tick_rate: float = float(1)
    slider_scoring_point_distance: float = 100 * float(1.4) / float(1)

    # HitObjects
    circle_count: int = 0
    slider_count: int = 0
    spinner_count: int = 0
    hit_objects: List[HitObject] = field(default_factory=list)

    # Colours
    custom_colours: bool = False

    # Others
    beatmap_version: int = 14
    control_points: List[ControlPoint] = field(default_factory=list)
