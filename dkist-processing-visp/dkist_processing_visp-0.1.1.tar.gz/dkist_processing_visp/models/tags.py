from enum import Enum

from dkist_processing_common.models.tags import Tag


class VispStemName(str, Enum):
    beam = "BEAM"
    raster_step = "RASTER_STEP"  # The number of the current step within a raster scan
    modstate = "MODSTATE"


class VispTag(Tag):
    @classmethod
    def beam(cls, beam_num: int) -> str:
        return cls.format_tag(VispStemName.beam, beam_num)

    @classmethod
    def raster_step(cls, raster_scan_step_num: int) -> str:
        return cls.format_tag(VispStemName.raster_step, raster_scan_step_num)
