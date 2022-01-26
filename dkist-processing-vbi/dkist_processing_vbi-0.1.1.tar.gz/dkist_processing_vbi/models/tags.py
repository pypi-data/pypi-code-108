from enum import Enum

from dkist_processing_common.models.tags import Tag


class VbiStemName(str, Enum):
    current_spatial_step = "STEP"


class VbiTag(Tag):
    @classmethod
    def spatial_step(cls, step_num: int) -> str:
        return cls.format_tag(VbiStemName.current_spatial_step, step_num)
