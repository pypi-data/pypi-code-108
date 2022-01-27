from enum import Enum

from dkist_processing_common.models.constants import ConstantsBase


class VbiBudName(Enum):
    num_spatial_steps = "NUM_SPATIAL_STEPS"
    num_exp_per_dsp = "NUM_EXP_PER_DSP"
    gain_exposure_times = "GAIN_EXPOSURE_TIMES"
    observe_exposure_times = "OBSERVE_EXPOSURE_TIMES"


class VbiConstants(ConstantsBase):
    @property
    def num_spatial_steps(self) -> int:
        return self._db_dict[VbiBudName.num_spatial_steps.value]

    @property
    def gain_exposure_times(self) -> [float]:
        return self._db_dict[VbiBudName.gain_exposure_times.value]

    @property
    def observe_exposure_times(self) -> [float]:
        return self._db_dict[VbiBudName.observe_exposure_times.value]

    @property
    def num_exp_per_dsp(self) -> int:
        # This might never be used?
        return self._db_dict[VbiBudName.num_exp_per_dsp.value]
