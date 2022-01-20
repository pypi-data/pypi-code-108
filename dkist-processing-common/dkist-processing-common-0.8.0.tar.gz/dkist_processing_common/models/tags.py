"""
Components of the Tag model.  Stem + Optional Suffix = Tag
"""
from enum import Enum
from typing import Union

# This is here to avoid a circular import in parsers.time
EXP_TIME_ROUND_DIGITS: int = 6


class StemName(str, Enum):
    """
    Controlled list of Tag Stems
    """

    output = "OUTPUT"
    input = "INPUT"
    intermediate = "INTERMEDIATE"
    input_dataset = "INPUT_DATASET"
    frame = "FRAME"
    movie = "MOVIE"
    stokes = "STOKES"
    movie_frame = "MOVIE_FRAME"
    task = "TASK"
    cs_step = "CS_STEP"
    modstate = "MODSTATE"
    dsps_repeat = "DSPS_REPEAT"
    calibrated = "CALIBRATED"  # A flag to indicate the data has been calibrated but not yet output
    quality = "QUALITY"
    exposure_time = "EXP_TIME"
    quality_task = "QUALITY_TASK"


class Tag:
    """
    Controlled methods for creating tags from stems + optional suffixes
    """

    @staticmethod
    def format_tag(stem: Union[StemName, str], *parts):
        if isinstance(stem, Enum):
            stem = stem.value
        parts = [stem, *parts]
        return "_".join([str(part).upper() for part in parts])

    # Static Tags
    @classmethod
    def movie_frame(cls):
        return cls.format_tag(StemName.movie_frame)

    @classmethod
    def input(cls):
        return cls.format_tag(StemName.input)

    @classmethod
    def calibrated(cls) -> str:
        return cls.format_tag(StemName.calibrated)

    @classmethod
    def output(cls):
        return cls.format_tag(StemName.output)

    @classmethod
    def frame(cls):
        return cls.format_tag(StemName.frame)

    @classmethod
    def intermediate(cls):
        return cls.format_tag(StemName.intermediate)

    @classmethod
    def input_dataset(cls):
        return cls.format_tag(StemName.input_dataset)

    @classmethod
    def movie(cls):
        return cls.format_tag(StemName.movie)

    # Dynamic Tags
    @classmethod
    def task(cls, ip_task_type: str):
        return cls.format_tag(StemName.task, ip_task_type)

    @classmethod
    def cs_step(cls, n: int):
        return cls.format_tag(StemName.cs_step, n)

    @classmethod
    def modstate(cls, n: int):
        return cls.format_tag(StemName.modstate, n)

    @classmethod
    def stokes(cls, stokes_state: str) -> str:
        return cls.format_tag(StemName.stokes, stokes_state)

    @classmethod
    def dsps_repeat(cls, dsps_repeat_number: int):
        return cls.format_tag(StemName.dsps_repeat, dsps_repeat_number)

    @classmethod
    def quality(cls, quality_metric: str) -> str:
        return cls.format_tag(StemName.quality, quality_metric)

    @classmethod
    def exposure_time(cls, exposure_time_s: float) -> str:
        return cls.format_tag(
            StemName.exposure_time, round(float(exposure_time_s), EXP_TIME_ROUND_DIGITS)
        )

    @classmethod
    def quality_task(cls, quality_task_type: str) -> str:
        return cls.format_tag(StemName.quality_task, quality_task_type)
