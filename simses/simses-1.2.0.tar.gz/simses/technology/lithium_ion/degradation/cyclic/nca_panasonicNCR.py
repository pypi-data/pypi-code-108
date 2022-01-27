from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class PanasonicNCACyclicDegradationModel(CyclicDegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector):
        super().__init__(cell_type, cycle_detector)
        self.__log: Logger = Logger(type(self).__name__)
        self.__capacity_loss = 0
        self.__capacity_loss_cyclic = cell_type.get_cyclic_capacity_loss_start()
        self.__fec = 0
        self.__rinc_cyclic = 0
        self.__resistance_increase = 0

        #  Aging Model based on:
        #  Geng, Yuhui (2019): Aging Model of Lithium-ion Battery. Master Thesis. Technical University Munich, EES.

        self.__A_QLOSS = 0.007043  # constant
        self.__B_QLOSS = -0.008682  # constant
        self.__C_QLOSS = 0.005818  # constant
        self.__D_QLOSS = 0.001892  # constant
        self.__E_QLOSS = 0
        self.__F_QLOSS = -0.001609

        self.__A_RINC = -0.09964  # constant
        self.__B_RINC = 0.03746  # constant
        self.__C_RINC = 0.01577  # constant
        self.__D_RINC = -0.001825  # constant
        self.__E_RINC = 0.001612  # constant
        self.__F_RINC = -0.006829  # constant

        self.__voltage_last_step = 3.6

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        crate: float = self._cycle_detector.get_crate() * 3600 # in 1 / s -> *3600 -> in 1/h
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle() # Delta EFC
        self.__fec = self._cycle_detector.get_full_equivalent_cycle() # Updating FEC

        qloss: float = self.__capacity_loss_cyclic # in p.u.

        # Open circuit voltage is used for cyclic degradation model
        voltage: float = self._cell.get_open_circuit_voltage(battery_state) / self._cell.get_serial_scale()
        v_ch = max(self.__voltage_last_step, voltage)  # charge voltage -> defined as higher one of both
        v_disch = min(self.__voltage_last_step, voltage)  # charge voltage -> defined as lower one of both

        if crate < 0.3571:
            virtual_fec: float = (qloss / (self.__A_QLOSS + self.__B_QLOSS * v_ch + self.__C_QLOSS * v_disch +
                                           self.__D_QLOSS * v_ch ** 2 + self.__F_QLOSS * v_ch * v_disch)) ** (4 / 3)
            rel_capacity_loss = lambda fec: (self.__A_QLOSS + self.__B_QLOSS * v_ch + self.__C_QLOSS * v_disch +
                                             self.__D_QLOSS * v_ch ** 2 + self.__F_QLOSS * v_ch * v_disch) * fec ** 0.75

            fec = virtual_fec + delta_fec
            capacity_loss = rel_capacity_loss(fec) - self.__capacity_loss_cyclic
        else:
            virtual_fec: float = (qloss / ((1 + (crate - 0.3571) / (0.3571*3)) *
                                           (self.__A_QLOSS + self.__B_QLOSS * v_ch + self.__C_QLOSS * v_disch +
                                            self.__D_QLOSS * v_ch ** 2 + self.__F_QLOSS * v_ch * v_disch))) ** (4 / 3)
            rel_capacity_loss = lambda fec: (1 + (crate - 0.3571) / (3*0.3571)) * \
                                            (self.__A_QLOSS + self.__B_QLOSS * v_ch + self.__C_QLOSS * v_disch +
                                             self.__D_QLOSS * v_ch ** 2 + self.__F_QLOSS * v_ch * v_disch) * fec ** 0.75

            fec = virtual_fec + delta_fec
            capacity_loss = rel_capacity_loss(fec) - self.__capacity_loss_cyclic

        self.__capacity_loss_cyclic += capacity_loss  # p.u.
        self.__capacity_loss = capacity_loss * self._cell.get_nominal_capacity()  # in Ah

        self.__voltage_last_step = voltage # save voltage for next calculation

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle()  # Delta EFC
        rinc: float = self.__rinc_cyclic # in p.u.

        # Open circuit voltage is used for cyclic degradation model
        voltage: float = self._cell.get_open_circuit_voltage(battery_state) / self._cell.get_serial_scale()
        v_ch = max(self.__voltage_last_step, voltage)  # charge voltage -> defined as higher one of both
        v_disch = min(self.__voltage_last_step, voltage)  # charge voltage -> defined as lower one of both

        virtual_fec = rinc / (
                self.__A_RINC + self.__B_RINC * v_ch + self.__C_RINC * v_disch + self.__D_RINC * v_ch ** 2 +
                self.__E_RINC * v_ch * v_disch + self.__F_RINC * v_disch ** 2)

        rel_resistance_increase = lambda fec: (self.__A_RINC + self.__B_RINC * v_ch + self.__C_RINC * v_disch +
                                               self.__D_RINC * v_ch ** 2 + self.__E_RINC * v_ch * v_disch +
                                               self.__F_RINC * v_disch ** 2) * fec

        resistance_increase = rel_resistance_increase(virtual_fec + delta_fec) - self.__rinc_cyclic

        if resistance_increase < 0: # No data for resistance increase at low SOC. For further information see
            # Geng, Yuhui (2019): Aging Model of Lithium-ion Battery. Master Thesis. Technical University Munich, EES.
            self.__log.warn('NCA cyclic resistance increase model is invalid when: 1. both charge and discharge voltage'
                            ' are close to lower operation voltage limit; 2. by high DoD (> 50 %). In this case'
                            ' the resistance increase is set to 0 for current timestep')
        resistance_increase = max(resistance_increase, 0)

        self.__rinc_cyclic += resistance_increase

        self.__resistance_increase = resistance_increase  # pu

    def get_degradation(self) -> float:
        capacity_loss = self.__capacity_loss
        self.__capacity_loss = 0  # Set value to 0, because cyclic losses are not calculated in each step
        return capacity_loss

    def get_resistance_increase(self) -> float:
        resistance_increase = self.__resistance_increase
        self.__resistance_increase = 0  # Set value to 0, because cyclic losses are not calculated in each step
        return resistance_increase

    def reset(self, lithium_ion_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        self.__capacity_loss_cyclic = 0
        self.__fec = 0
        self.__rinc_cyclic = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        self.__log.close()
