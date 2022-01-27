from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import CyclicDegradationModel

import numpy as np


class LFPGenericCyclicDegradationModel(CyclicDegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector):
        super().__init__(cell_type, cycle_detector)
        self.__capacity_loss = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()
        self.__log: Logger = Logger(type(self).__name__)

        # parameters
        self.__z = 0.392611936548533
        self.__a = 1.06456066666941
        self.__b = -10931.5112862013
        self.__c = 1
        self.__d = 1
        self.__e = -4.11988721392584
        self.__f = 1.70180851471426
        self.__g = 1.81362732352495
        self.__h = -0.217897784225967
        self.__i = 0.0201876349197979
        self.__j = -0.0382242087224787
        self.__k = 0.0185488829889972
        self.__l = 0.00326042032279996
        self.__m = 0.313675037732425
        self.__n = 1.90274120973485

        # constants
        self.__R = 8.314462  # universal gas constant

    def fec_dependency(self, fec):
        # degradation depends on fec as a power law function
        return fec**self.__z

    def temperature_dependency(self, temp):
        # degradation depends on temperature as arrhenius function
        return self.__a * np.exp(- self.__b / (self.__R * temp))

    def mean_soc_dependency(self, msoc):
        # degradation depends on msoc as a cubic function
        # limit msoc to avoid negative function values
        # implement warnings
        if msoc > 0.75:
            msoc = 0.75
            self.__log.warn('Mean state of charge for detected cycle was above 75%. MSoC was set to 75% to avoid '
                            'negative degradation.')
        elif msoc < 0.25:
            msoc = 0.25
            self.__log.warn('Mean state of charge for detected cycle was below 25%. MSoC was set to 25% to avoid '
                            'negative degradation.')
        return self.__e * msoc**3 + self.__f * msoc**2 + self.__g * msoc + self.__h

    def doc_dependency(self, doc):
        # degradation depends on doc as a cubic function
        return self.__i * doc**3 + self.__j * doc**2 + self.__k * doc + self.__l

    def crate_dependency(self, crate):
        # degradation depends on crate as a linear function
        return self.__m * crate + self.__n

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        c_rate: float = self._cycle_detector.get_crate() * 3600
        depth_of_discharge: float = self._cycle_detector.get_depth_of_cycle()
        full_equivalent_cycle: float = self._cycle_detector.get_full_equivalent_cycle()
        mean_soc: float = self._cycle_detector.get_mean_soc()
        temperature: float = battery_state.temperature
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle()

        # calculate degradation in percent (divide by 100 to get p.u.) with function 11 from MA Sandner
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
