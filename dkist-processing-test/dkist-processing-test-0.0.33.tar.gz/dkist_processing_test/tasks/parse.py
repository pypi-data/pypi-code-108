from typing import List
from typing import TypeVar

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.tasks import ParseL0InputData

S = TypeVar("S", bound=Stem)


class TotalDspsRepeatsBud(UniqueBud):
    def __init__(self):
        super().__init__(
            constant_name=BudName.num_dsps_repeats.value, metadata_key="num_dsps_repeats"
        )

    def setter(self, fits_obj: L0FitsAccess):
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return super().setter(fits_obj)


class DspsRepeatNumberFlower(SingleValueSingleKeyFlower):
    def __init__(self):
        super().__init__(
            tag_stem_name=StemName.dsps_repeat.value, metadata_key="current_dsps_repeat"
        )

    def setter(self, fits_obj: L0FitsAccess):
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return super().setter(fits_obj)


class ParseL0TestInputData(ParseL0InputData):
    @property
    def fits_parsing_class(self):
        return L0FitsAccess

    @property
    def tag_flowers(self) -> List[S]:
        return super().tag_flowers + [
            SingleValueSingleKeyFlower(
                tag_stem_name=StemName.task.value, metadata_key="ip_task_type"
            ),
            DspsRepeatNumberFlower(),
        ]

    @property
    def constant_flowers(self) -> List[S]:
        return super().constant_flowers + [TotalDspsRepeatsBud()]
