from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.spectral_line import find_associated_line
from dkist_processing_common.parsers.unique_bud import UniqueBud

from dkist_processing_visp.models.spectral_line import VISP_SPECTRAL_LINES
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class SpectralLineBud(UniqueBud):
    def __init__(self):
        super().__init__(constant_name=BudName.spectral_line.value, metadata_key="wavelength")

    def setter(self, fits_obj: VispL0FitsAccess):
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return find_associated_line(wavelength=fits_obj.wavelength, lines=VISP_SPECTRAL_LINES)
