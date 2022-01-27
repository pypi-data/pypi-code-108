import scipy.integrate as integrate
import pandas as pd
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel
from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig


class SonyLFPCyclicDegradationModel(CyclicDegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_data_config: BatteryDataConfig,
                 battery_config: BatteryConfig):
        super().__init__(cell_type, cycle_detector)
        self.__log: Logger = Logger(type(self).__name__)
        self.__capacity_loss = 0
        self.__capacity_loss_cyclic = cell_type.get_cyclic_capacity_loss_start()
        self.__resistance_increase = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()

        # Source SONY_US26650FTC1_Product Specification and Naumann, Maik, Franz Spingler, and Andreas Jossen.
        # "Analysis and modeling of cycle aging of a commercial LiFePO4/graphite cell."
        # Journal of Power Sources 451 (2020): 227666.
        # DOI: https://doi.org/10.1016/j.jpowsour.2019.227666

        # # original parameters
        # self.__A_QLOSS = 0.0630  # constant
        # self.__B_QLOSS = 0.0971  # constant
        # self.__C_QLOSS = 4.0253  # constant
        # self.__D_QLOSS = 1.0923  # constant
        #
        # self.__A_RINC = -0.0020  # constant
        # self.__B_RINC = 0.0021  # constant
        # self.__C_RINC = 6.8477  # constant
        # self.__D_RINC = 0.91882  # constant

        # read in parameters from CSV
        model_number = battery_config.degradation_model_number
        values_cap_model = pd.read_csv(battery_data_config.lfp_sony_degradation_capacity_file,
                                       skiprows=lambda x: x not in [0, model_number]).values.tolist()[0]
        values_res_model = pd.read_csv(battery_data_config.lfp_sony_degradation_resistance_file,
                                       skiprows=lambda x: x not in [0, model_number]).values.tolist()[0]
        # print("\nUsing the following cyc degradation model: \tNumber: " + str(model_number) + "\tIdentifier: " +
        #       values_cap_model[0])
        self.__A_QLOSS = values_cap_model[5]  # constant
        self.__B_QLOSS = values_cap_model[6]  # constant
        self.__C_QLOSS = values_cap_model[7]  # constant
        self.__D_QLOSS = values_cap_model[8]  # constant

        self.__A_RINC = values_res_model[5]  # constant
        self.__B_RINC = values_res_model[6]  # constant
        self.__C_RINC = values_res_model[7]  # constant
        self.__D_RINC = values_res_model[8]  # constant

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        crate: float = self._cycle_detector.get_crate() * 3600  # in 1 / s -> *3600 -> in 1/h
        doc: float = self._cycle_detector.get_depth_of_cycle()  # in pu
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle()  # in pu
        qloss: float = (self.__initial_capacity - battery_state.capacity / battery_state.nominal_voltage) / self.__initial_capacity  # pu

        # calculate stress factor dependent coefficients
        k_c_rate_qloss = self.__A_QLOSS * crate + self.__B_QLOSS
        k_doc_qloss = self.__C_QLOSS * (doc - 0.6)**3 + self.__D_QLOSS

        # calculate capacity loss based on virtual FEC and past total degradation.
        virtual_fec: float = (qloss * 100 / (k_c_rate_qloss * k_doc_qloss))**2
        capacity_loss = k_c_rate_qloss * k_doc_qloss * (virtual_fec + delta_fec)**0.5 / 100  # total cyc. qloss in p.u.
        capacity_loss -= qloss  # relative qloss in pu in current timestep

        # # calculate capacity loss based on virtual FEC and past cyclic degradation.
        # virtual_fec: float = (self.__capacity_loss_cyclic * 100 / (k_c_rate_qloss * k_doc_qloss))**2
        # capacity_loss = k_c_rate_qloss * k_doc_qloss * (virtual_fec + delta_fec)**0.5 / 100  # total cyc. qloss in p.u.
        # capacity_loss -= self.__capacity_loss_cyclic  # relative qloss in pu in current timestep
        # self.__capacity_loss_cyclic += capacity_loss

        self.__capacity_loss = capacity_loss * self.__initial_capacity  # Ah

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        crate: float = self._cycle_detector.get_crate() * 3600  # in 1 / s -> *3600 -> in 1/h
        doc: float = self._cycle_detector.get_depth_of_cycle()  # in pu
        delta_fec: float = self._cycle_detector.get_delta_full_equivalent_cycle()  # in pu

        # calculate stress factor dependent coefficients
        k_c_rate_rinc = self.__A_RINC * crate + self.__B_RINC
        k_doc_rinc = self.__C_RINC * (doc - 0.5)**3 + self.__D_RINC

        # calculate resistance increase
        resistance_increase = k_c_rate_rinc * k_doc_rinc * delta_fec
        self.__resistance_increase = resistance_increase / 100  # in pu

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
