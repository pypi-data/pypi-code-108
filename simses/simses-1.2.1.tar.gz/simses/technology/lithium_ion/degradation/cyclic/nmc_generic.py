from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import CyclicDegradationModel


class NMCGenericCyclicDegradationModel(CyclicDegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector):
        super().__init__(cell_type, cycle_detector)
        self.__capacity_loss = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()

        # parameters old
        # self.__z = 0.705799526688744
        # self.__a = -0.0305245206114891
        # self.__b = 27.6760345173264
        # self.__c = -8353.74758895471
        # self.__d = 839529.464749593
        # self.__e = -1.03958438129589
        # self.__f = 2.95820190976433
        # self.__g = -2.06426540159782
        # self.__h = 0.436349803729391
        # self.__i = -0.183172940789106
        # self.__j = 3.77584036178456
        # self.__k = -2.02237532152262
        # self.__l = 0.256120170615456
        # self.__m = 0.000819809707717746
        # self.__n = 0.0302888311700094

        # parameters new
        self.__z = 0.671627179869084
        self.__a = 2.9957641942448E-07
        self.__b = -0.0000720878146452049
        self.__c = -0.0385306420008836
        self.__d = 9.99999995479674
        self.__e = -3.02499312835016
        self.__f = 8.81907826557735
        self.__g = -6.19696246135569
        self.__h = 1.31642579445754
        self.__i = -1.24637880290245
        self.__j = 9.95196984230208
        self.__k = -5.69035010249573
        self.__l = 0.870681264163946
        self.__m = 0.270719035641741
        self.__n = 9.99676141875715

    def fec_dependency(self, fec):
        # degradation depends on fec as a power law function
        return fec**self.__z

    def temperature_dependency(self, temp):
        # degradation depends on temperature as a cubic function
        return self.__a * temp**3 + self.__b * temp**2 + self.__c * temp + self.__d

    def mean_soc_dependency(self, msoc):
        # degradation depends on msoc as a cubic function
        return self.__e * msoc**3 + self.__f * msoc**2 + self.__g * msoc + self.__h

    def doc_dependency(self, doc):
        # degradation depends on doc as a cubic function
        return self.__i * doc ** 3 + self.__j * doc ** 2 + self.__k * doc + self.__l

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

        # calculate degradation in percent (divide by 100 to get p.u.) with function 29 from MA Sandner
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
