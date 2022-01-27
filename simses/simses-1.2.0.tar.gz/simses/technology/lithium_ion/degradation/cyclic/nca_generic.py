from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import CyclicDegradationModel

import numpy as np


class NCAGenericCyclicDegradationModel(CyclicDegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector):
        super().__init__(cell_type, cycle_detector)
        self.__capacity_loss = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()

        # parameters
        self.__z = 0.172396498182181
        self.__a = -6.4598243817573E-07
        self.__b = 0.000159249929508653
        self.__c = 0.0162972227060786
        self.__d = 1.22012389207326
        self.__e = 0.291743390220046
        self.__f = 0.29174367528008
        self.__g = 0.291694646922772
        self.__h = 0.291609580760524
        self.__i = 0.000440503468592159
        self.__j = 0.235399850460447
        self.__k = 1
        self.__l = 1
        self.__m = 0.0927398171669826
        self.__n = 1

        # constants
        self.__R = 8.314462  # universal gas constant

    def fec_dependency(self, fec):
        # degradation depends on fec as a power law function
        return fec**self.__z

    def temperature_dependency(self, temp):
        # degradation depends on temperature as a cubic function
        return self.__a * temp ** 3 + self.__b * temp ** 2 + self.__c * temp + self.__d

    def mean_soc_dependency(self, msoc):
        # degradation depends on msoc as a cubic function
        return self.__e * msoc**3 + self.__f * msoc**2 + self.__g * msoc + self.__h

    def doc_dependency(self, doc):
        # degradation depends on doc as an exponential function
        return np.exp(self.__i * doc)

    def crate_dependency(self, crate):
        # degradation depends on crate as an exponential function
        return np.exp(self.__m * crate)

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        c_rate: float = self._cycle_detector.get_crate() * 3600
        depth_of_discharge: float = self._cycle_detector.get_depth_of_cycle()
        full_equivalent_cycle: float = self._cycle_detector.get_full_equivalent_cycle()
        mean_soc: float = self._cycle_detector.get_mean_soc()
        temperature: float = battery_state.temperature
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle()

        # calculate degradation in percent (divide by 100 to get p.u.) with function 26 from MA Sandner
        capacity_loss_after = self.fec_dependency(full_equivalent_cycle) * \
                              self.temperature_dependency(temperature) * \
                              self.mean_soc_dependency(mean_soc) * \
                              self.doc_dependency(depth_of_discharge) * \
                              self.crate_dependency(c_rate)
        capacity_loss_before = self.fec_dependency(full_equivalent_cycle - delta_fec) * \
                               self.temperature_dependency(temperature) * \
                               self.mean_soc_dependency(mean_soc) * \
                               self.doc_dependency(depth_of_discharge) * \
                               self.crate_dependency(c_rate)

        self.__capacity_loss = (capacity_loss_after - capacity_loss_before) / 100.0 * self.__initial_capacity

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        # no resistance increase calculated for generic degradation model
        pass

    def get_degradation(self) -> float:
        degradation = self.__capacity_loss
        self.__capacity_loss = 0
        return degradation

    def get_resistance_increase(self) -> float:
        # no resistance increase calculated for generic degradation model
        return 0

    def reset(self, lithium_ion_state: LithiumIonState) -> None:
        self.__capacity_loss = 0

    def close(self) -> None:
        pass
