from abc import ABC

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.tasks import ScienceTaskL0ToL1Base

from dkist_processing_vbi.models.constants import VbiBudName


class VbiScienceTask(ScienceTaskL0ToL1Base, ABC):
    @property
    def num_spatial_steps(self) -> int:
        return self.constants[VbiBudName.num_spatial_steps.value]

    @property
    def dark_exposure_times(self) -> [float]:
        return self.constants[BudName.dark_exposure_times.value]

    @property
    def gain_exposure_times(self) -> [float]:
        return self.constants[VbiBudName.gain_exposure_times.value]

    @property
    def observe_exposure_times(self) -> [float]:
        return self.constants[VbiBudName.observe_exposure_times.value]
