from enum import Enum

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase


class VispBudName(Enum):
    num_raster_steps = "NUM_RASTER_STEPS"
    polarimeter_mode = "POLARIMETER_MODE"
    wavelength = "WAVELENGTH"
    lamp_exposure_times = "LAMP_EXPOSURE_TIMES"
    solar_exposure_times = "SOLAR_EXPOSURE_TIMES"
    observe_exposure_times = "OBSERVE_EXPOSURE_TIMES"
    polcal_exposure_times = "POLCAL_EXPOSURE_TIMES"


class VispConstants(ConstantsBase):
    @property
    def wavelength(self) -> float:
        return self._db_dict[VispBudName.wavelength.value]

    @property
    def num_modstates(self):
        return self._db_dict[BudName.num_modstates.value]

    @property
    def num_beams(self):
        """
        The VISP will always have two beams
        """
        return 2

    @property
    def num_cs_steps(self):
        return self._db_dict[BudName.num_cs_steps.value]

    @property
    def num_raster_steps(self):
        return self._db_dict[VispBudName.num_raster_steps.value]

    @property
    def correct_for_polarization(self):
        return self._db_dict[VispBudName.polarimeter_mode.value] == "observe_polarimetric"

    @property
    def num_spatial_bins(self) -> int:
        return 1

    @property
    def num_spectral_bins(self) -> int:
        return 1

    @property
    def lamp_exposure_times(self) -> [float]:
        return self._db_dict[VispBudName.lamp_exposure_times.value]

    @property
    def solar_exposure_times(self) -> [float]:
        return self._db_dict[VispBudName.solar_exposure_times.value]

    @property
    def polcal_exposure_times(self) -> [float]:
        if self.correct_for_polarization:
            return self._db_dict[VispBudName.polcal_exposure_times.value]
        else:
            return []

    @property
    def observe_exposure_times(self) -> [float]:
        return self._db_dict[VispBudName.observe_exposure_times.value]
