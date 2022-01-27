from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class SanyoNMCCyclicDegradationModel(CyclicDegradationModel):
    """Source: Schmalstieg, J., Käbitz, S., Ecker, M., & Sauer, D. U. (2014).
    A holistic aging model for Li (NiMnCo) O2 based 18650 lithium-ion batteries.
    Journal of Power Sources, 257, 325-334."""

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector):
        super().__init__(cell_type, cycle_detector)
        self.__log: Logger = Logger(type(self).__name__)
        self.__capacity_loss = 0
        self.__resistance_increase = 0
        self.__voltage_last_step_capacity = 3.6
        self.__voltage_last_step_resistance = 3.6
        self.__cycle_detector: CycleDetector = cycle_detector
        self.__ah_throughput_total_cap = 0

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        # get doc, delta charge throughput and average voltage between cycles
        doc = self._cycle_detector.get_depth_of_cycle()
        qcell = battery_state.capacity / battery_state.nominal_voltage / self._cell.get_parallel_scale()
        delta_ah_throughput = qcell*doc
        voltage = self._cell.get_open_circuit_voltage(battery_state) / self._cell.get_serial_scale()
        v_average = (self.__voltage_last_step_capacity + voltage) / 2
        self.__voltage_last_step_capacity = voltage

        beta_cap = 7.348*10**(-3)*(v_average - 3.667)**2 + 7.6*10**(-4) + 4.081*10**(-3)*doc
        # implementation of discretization method as in MA Chuanqin Ni
        total_capacity_t1 = 1 - beta_cap * self.__ah_throughput_total_cap ** 0.5  # in p.u.
        total_capacity_t2 = 1 - beta_cap * (self.__ah_throughput_total_cap + delta_ah_throughput) ** 0.5  # in p.u.
        capacity_loss = total_capacity_t1 - total_capacity_t2

        self.__ah_throughput_total_cap += delta_ah_throughput
        self.__capacity_loss = capacity_loss * self._cell.get_nominal_capacity()  # Ah

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        # get doc, delta charge throughput and average voltage between cycles
        doc = self._cycle_detector.get_depth_of_cycle()
        qcell = battery_state.capacity / battery_state.nominal_voltage / self._cell.get_parallel_scale()
        delta_ah_throughput = qcell * doc
        voltage = self._cell.get_open_circuit_voltage(battery_state) / self._cell.get_serial_scale()
        v_average = (self.__voltage_last_step_resistance + voltage) / 2
        self.__voltage_last_step_resistance = voltage

        beta_res = 2.153*10**(-4)*(v_average - 3.725)**2 - 1.521*10**(-5) + 2.798*10**(-4)*doc
        # implementation of discretization method as in MA Chuanqin Ni
        resistance_increase = beta_res * delta_ah_throughput # in p.u.

        self.__resistance_increase = resistance_increase  # pu

    def get_degradation(self) -> float:
        capacity_loss = self.__capacity_loss
        self.__capacity_loss = 0    # Set value to 0, because cyclic losses are not calculated in each step
        return capacity_loss

    def get_resistance_increase(self) -> float:
        resistance_increase = self.__resistance_increase
        self.__resistance_increase = 0 # Set value to 0, because cyclic losses are not calculated in each step
        return resistance_increase

    def reset(self, lithium_ion_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        self.__log.close()