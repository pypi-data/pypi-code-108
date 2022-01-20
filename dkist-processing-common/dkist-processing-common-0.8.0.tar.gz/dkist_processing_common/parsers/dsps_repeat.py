from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import UniqueBud


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
