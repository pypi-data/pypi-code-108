from __future__ import annotations

from typing import Type
from typing import Union

from astropy.time import Time

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class CSStep:
    """This class allows for an easy way to quickly compare fits access objects to determine if they come from the
    same Calibration Sequence (CS) step. Each step in a CS is defined by the configuration of the GOS, namely the
    status of the polarizer and retarder (in or out) and the angle of each. Because some CS schemes call for some
    GOS configurations to repeat a check is also made against the observation time for each object; the default in
    the parameter store defines a maximum difference in time where two exposures are considered different CS steps
    regardless of GOS configuration.

    This class can also be sorted. In this case, only the observation time is taken into account.

    Finally, this class is hashable for use in dictionaries. The hash is only based on the GOS configuration so that
    all objects from the same CS step result in the same hash. Python also checks that dictionary keys are equal so any
    conflicts with repeated CS steps are avoided.
    """

    def __init__(self, fits_obj: L0FitsAccess, max_cs_time_sec: float):
        """Initialize and read the GOS configuration and time from a SPEC-0122 FITS header.

        Parameters
        ----------
        fits_obj
            The FitsAccess object to ingest
        max_cs_time_sec
            Any objects taken more than this amount of time apart are considered in separate steps, regardless of GOS
            configuration.
        """
        self.pol_in = fits_obj.gos_polarizer_status not in ["undefined", "clear"]
        self.pol_theta = fits_obj.gos_polarizer_angle
        self.ret_in = fits_obj.gos_retarder_status not in ["undefined", "clear"]
        self.ret_theta = fits_obj.gos_retarder_angle
        self.dark_in = fits_obj.gos_level0_status == "DarkShutter"
        self.obs_time = Time(fits_obj.time_obs)
        self.max_cs_time_sec = max_cs_time_sec

        self.max_cs_time_sec = max_cs_time_sec

    def __repr__(self):
        return f"CS step taken on {self.obs_time.fits}"

    def __str__(self):
        return "CS step with Pol = {}:{}, Ret = {}:{}, Dark = {}. Taken at {}".format(
            self.pol_in,
            self.pol_theta,
            self.ret_in,
            self.ret_theta,
            self.dark_in,
            self.obs_time.fits,
        )

    def __eq__(self, other: object) -> bool:
        """Two steps are equal if they have the same GOS configuration and are taken within some package-defined time
        of each other."""
        if not isinstance(other, CSStep):
            raise TypeError(f"Cannot compare CSStep with type {type(other)}")

        for item in ["pol_in", "pol_theta", "ret_in", "ret_theta", "dark_in"]:
            if getattr(self, item) != getattr(other, item):
                return False

        tdelt = abs(self.obs_time - other.obs_time)
        if tdelt.sec > self.max_cs_time_sec:
            return False

        return True

    def __lt__(self, other: CSStep) -> bool:
        """Only based on time"""
        return self.obs_time < other.obs_time

    def __hash__(self) -> int:
        """Only based on GSO configuration so that all objects from the same CS step hash the same"""
        return hash((self.pol_in, self.pol_theta, self.ret_in, self.ret_theta, self.dark_in))


class CSStepFlower(Stem):
    """ Identify which CS Step a header belongs to """

    def __init__(self, max_cs_step_time_sec: float):
        super().__init__(stem_name=StemName.cs_step.value)
        self.max_cs_step_time_sec = max_cs_step_time_sec

    def setter(self, fits_obj: L0FitsAccess) -> Union[CSStep, Type[SpilledDirt]]:
        if fits_obj.ip_task_type != "polcal":
            return SpilledDirt
        return CSStep(fits_obj, max_cs_time_sec=self.max_cs_step_time_sec)

    def getter(self, key) -> Union[str, float, int]:
        unique_steps = sorted(list(set(self.key_to_petal_dict.values())))
        return unique_steps.index(self.key_to_petal_dict[key])


class NumCSStepBud(Stem):
    """ The total number of CS Steps present in a dataset """

    def __init__(self, max_cs_step_time_sec: float):
        super().__init__(stem_name=BudName.num_cs_steps.value)
        self.max_cs_step_time_sec = max_cs_step_time_sec

    def setter(self, fits_obj: L0FitsAccess) -> Union[CSStep, Type[SpilledDirt]]:
        if fits_obj.ip_task_type != "polcal":
            return SpilledDirt
        return CSStep(fits_obj, max_cs_time_sec=self.max_cs_step_time_sec)

    def getter(self, key) -> int:
        value_set = set(self.key_to_petal_dict.values())
        return len(value_set)
