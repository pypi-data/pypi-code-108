from typing import Hashable

"""
Time parser
"""
from typing import Union

import numpy as np
from astropy.time import Time

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import StemName, EXP_TIME_ROUND_DIGITS
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import UniqueBud


class TimeBud(UniqueBud):
    """
    Base class for all Time Buds
    """

    def __init__(self, constant_name: str):
        super().__init__(constant_name, metadata_key="time_obs")

    def setter(self, fits_obj: L0FitsAccess) -> Union[float, SpilledDirt]:
        """
        If the file is an observe file, its DATE-OBS value is stored as unix seconds
        """
        if fits_obj.ip_task_type == "observe":
            return Time(getattr(fits_obj, self.metadata_key)).unix
        return SpilledDirt


class AverageCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.average_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the mean cadence between frames
        """
        return np.mean(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MaximumCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.maximum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the maximum cadence between frames
        """
        return np.max(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MinimumCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.minimum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the minimum cadence between frames
        """
        return np.min(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class VarianceCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.variance_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the cadence variance between frames
        """
        return np.var(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class ExposureTimeFlower(SingleValueSingleKeyFlower):
    """For tagging the frame exposure time.

    Different than SingleValueSingleKeyFlower because we round to avoid jitter in the headers
    """

    def __init__(self):
        super().__init__(
            tag_stem_name=StemName.exposure_time.value, metadata_key="fpa_exposure_time_sec"
        )

    def setter(self, fits_obj: L0FitsAccess):
        raw_exp_time = super().setter(fits_obj)
        return round(raw_exp_time, EXP_TIME_ROUND_DIGITS)


class TaskExposureTimesBud(Stem):
    """Produce a tuple of all exposure times present in the dataset for a specific ip task type"""

    def __init__(self, stem_name: str, ip_task_type: str):
        super().__init__(stem_name=stem_name)
        self.metadata_key = "fpa_exposure_time_sec"
        self.ip_task_type = ip_task_type

    def setter(self, fits_obj: L0FitsAccess):
        if fits_obj.ip_task_type.lower() == self.ip_task_type.lower():
            raw_exp_time = getattr(fits_obj, self.metadata_key)
            return round(raw_exp_time, EXP_TIME_ROUND_DIGITS)
        return SpilledDirt

    def getter(self, key: Hashable) -> Hashable:
        exp_time_tup = tuple(sorted(set(self.key_to_petal_dict.values())))
        return exp_time_tup
