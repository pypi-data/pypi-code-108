from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.parsers.unique_bud import UniqueBud

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.visp_l0_fits_access import VispL0FitsAccess


class PolarimeterModeBud(UniqueBud):
    def __init__(self):
        super().__init__(
            constant_name=VispBudName.polarimeter_mode.value, metadata_key="polarimeter_mode"
        )

    def setter(self, fits_obj: VispL0FitsAccess):
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return super().setter(fits_obj)
