from replifactory.culture.blank import BlankCulture
import numpy as np
import os
from replifactory.culture.culture_functions import inoculate


class BatchCulture(BlankCulture):

    """
    class for subjecting the culture to a constantly increasing stress level (e.g. 5% per generation)
    useful for rapidly increasing the stress (relative to an evolutionary timespan)
    and determining the fitness before significant evolutionary changes occur.

        EXAMPLE:
    culture = EnduranceStressCulture(directory="./NewExperiment/", vial_number=1,
                                     name="Species 1", description="Strain 1", device=None,
                                     default_dilution_volume=10, dead_volume=15, od_max_limit=0.3,
                                     stress_increase_per_generation=1.05, initial_generations=3)
    """
    pumps = []

    def __init__(self, directory: str = None, vial_number: int = None, name: str = "Species 1",
                 description: str = "Strain 1"):
        # Running parameters
        self._mu = None
        self._mu_error = None
        self._t_doubling = None
        self._t_doubling_error = None
        self._inoculation_time = None
        self._samples_collected = {}
        self._is_aborted = False
        self._mu_max_measured = 0
        self._t_doubling_min_measured = np.inf
        super().__init__(directory=directory, vial_number=vial_number, name=name, description=description)
        del self.dead_volume

    def update(self):
        pass

    def check(self):
        assert self.device.is_connected()
        assert self.vial_number in [1, 2, 3, 4, 5, 6, 7]
        assert os.path.exists(self.directory)
        self.device.stirrers.check_calibration(self.vial_number)
        assert callable(self.device.od_sensors[self.vial_number].calibration_function)
        assert -0.3 < self.od_blank < 0.3

    def inoculate(self, name=None, description=None):
        inoculate(culture=self, name=name, description=description)
        self._mu_max_measured = 0
        self._t_doubling_min_measured = np.inf
        self._is_aborted = False
        self.save()
