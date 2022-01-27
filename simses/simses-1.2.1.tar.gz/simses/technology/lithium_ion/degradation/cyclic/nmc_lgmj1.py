import scipy.integrate as integrate
import math

from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel

# Source:
# Schindler M., Sturm J., Ludwig S., Durdel A., Jossen A.
# Comprehensive Analysis of the Aging Behavior of Nickel-Rich, Silicon-Graphite Lithium-Ion Cells Subject to Varying
# Temperature and Charging Profiles
# Journal of The Electrochemical Society, https://doi.org/10.1149/1945-7111/ac03f6

class LGMJ1_NMCCyclicDegradationModel(CyclicDegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector):
        super().__init__(cell_type, cycle_detector)
        self.__log: Logger = Logger(type(self).__name__)

        self.__capacity_loss = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()
        self.__capacity_loss_cyclic = cell_type.get_cyclic_capacity_loss_start()

        self.__A_QLOSS = 0.00751  # constant
        self.__B_QLOSS = -2.305  # constant

        self.__resistance_increase = 0
        self.__rinc_cyclic = 0

        self.__A_RINC = -0.006605  # constant
        self.__B_RINC = 2.005  # constant

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        qloss: float = self.__capacity_loss_cyclic  # in pu
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle()  # in pu
        temperature: float = battery_state.temperature  # in K
        # Data only available for 273.15 K, 293.15 K and 298.15 K
        # Therefore if Temperature is under/over 273.15 K/298.15 K the simulation uses 273.15 K/298.15 K

        if temperature < 273.15:
            temperature = 273.15
            self.__log.warn('Temperature is under 273.15K but the simulation used 273.15K.')
        if temperature > 298.15:
            temperature = 298.15
            self.__log.warn('Temperature is over 298.15K but the simulation used 298.15K.')

        virtual_fec: float = ((1-qloss) * 100 - 100) / (self.__A_QLOSS * temperature + self.__B_QLOSS)
        rel_capacity_status = lambda fec: ((self.__A_QLOSS * temperature + self.__B_QLOSS)*fec+100) / 100
        fec: float = virtual_fec + delta_fec
        capacity_loss = (1 - rel_capacity_status(fec)) - self.__capacity_loss_cyclic
        # Total cyclic capacity loss
        self.__capacity_loss_cyclic += capacity_loss  # in p.u.
        # Delta cyclic capacity loss
        self.__capacity_loss = capacity_loss * self._cell.get_nominal_capacity()  # in Ah

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        rinc: float = self.__rinc_cyclic
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle()  # in pu
        temperature: float = battery_state.temperature  # in K
        # Data only available for 273.15 K, 293.15 K and 298.15 K
        # Therefore if Temperature is under/over 273.15 K/298.15 K the simulation uses 273.15 K/298.15 K

        if temperature < 273.15:
            temperature = 273.15
            self.__log.warn('Temperature is under 273.15K but the simulation used 273.15K.')
        if temperature > 298.15:
            temperature = 298.15
            self.__log.warn('Temperature is over 298.15K but the simulation used 298.15K.')

        virtual_fec: float = (rinc * 100) / (self.__A_RINC * temperature + self.__B_RINC)
        rel_resistance_increase = lambda fec: ((self.__A_RINC * temperature + self.__B_RINC) * fec) / 100
        fec = virtual_fec + delta_fec
        resistance_increase = (rel_resistance_increase(fec)) - self.__rinc_cyclic
        self.__rinc_cyclic += resistance_increase
        self.__resistance_increase = resistance_increase

    def get_degradation(self) -> float:
        capacity_loss = self.__capacity_loss
        self.__capacity_loss = 0    # Set value to 0, because cyclic losses are not calculated in each step
        return capacity_loss

    def get_resistance_increase(self) -> float:
        resistance_increase = self.__resistance_increase
        self.__resistance_increase = 0  # Set value to 0, because cyclic losses are not calculated in each step
        return resistance_increase


    def reset(self, lithium_ion_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        self.__log.close()
