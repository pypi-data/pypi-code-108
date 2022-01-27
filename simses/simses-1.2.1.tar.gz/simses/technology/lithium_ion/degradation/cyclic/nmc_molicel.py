import math
import pandas as pd
import scipy.interpolate
from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class MolicelNMCCyclicDegradationModel(CyclicDegradationModel):
    # Values based on MA Ni Chuanqin (EES, TUM) and adapted from Yulong Zhao in order to have the same structure
    # as in the aging models of Maik Naumann (SonyLFP)
    __DOC_IDX = 0
    __LENGTH_DOC_ARRAY = 1001

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_data_config: BatteryDataConfig):
        super().__init__(cell_type, cycle_detector)
        self.__log: Logger = Logger(type(self).__name__)
        self.__capacity_loss = 0
        self.__capacity_loss_cyclic = cell_type.get_cyclic_capacity_loss_start()
        self.__rinc_cyclic = 0
        self.__resistance_increase = 0

        self.__A_QLOSS = 1.1587  # constant
        self.__B_QLOSS = 1.569  # constant
        self.__C_QLOSS = 0.5562  # constant

        self.__A_RINC = 0.5562  # constant

        capacity_cyc_file: str = battery_data_config.nmc_molicel_capacity_cyc_file
        capacity_cyc = pd.read_csv(capacity_cyc_file)  # -
        capacity_cyc_mat = capacity_cyc.iloc[:self.__LENGTH_DOC_ARRAY, 1]
        doc_arr = capacity_cyc.iloc[:, self.__DOC_IDX]
        self.__capacity_cyc_interp1d = scipy.interpolate.interp1d(doc_arr, capacity_cyc_mat, kind='linear')

        ri_cyc_file: str = battery_data_config.nmc_molicel_ri_cyc_file
        ri_cyc = pd.read_csv(ri_cyc_file)  # -
        ri_cyc_mat = ri_cyc.iloc[:(self.__LENGTH_DOC_ARRAY + 1), 1]
        doc_arr = ri_cyc.iloc[:, self.__DOC_IDX]
        self.__ri_cyc_interp1d = scipy.interpolate.interp1d(doc_arr, ri_cyc_mat, kind='linear')

        self.__cycle_detector: CycleDetector = cycle_detector

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        crate: float = self.__cycle_detector.get_crate() * 3600 # in 1 / s -> *3600 -> in 1/h
        doc: float = self.__cycle_detector.get_depth_of_cycle() # DOC

        qloss: float = self.__capacity_loss_cyclic  # only cyclic losses
        qcell: float = battery_state.capacity / battery_state.nominal_voltage/ self._cell.get_parallel_scale()
        # single cell capacity in Ah

        if crate <= -0.5:
            k_capacity_cyc = self.get_stressfkt_ca_cyc(doc) / self.__A_QLOSS * (self.__A_QLOSS) \
                             ** (math.log2(crate / (-0.5)))
        elif abs(crate) < 0.5:
            k_capacity_cyc = self.get_stressfkt_ca_cyc(doc)
        else:
            k_capacity_cyc = self.get_stressfkt_ca_cyc(doc) * self.__B_QLOSS ** (math.log2(crate / 0.5))

        if k_capacity_cyc == 0.0:
            virtual_ChargeThroughput: float = 0
        else:
            virtual_ChargeThroughput: float = (qloss / k_capacity_cyc)**(1 / self.__C_QLOSS)

        capacity_loss = max(0,
                            k_capacity_cyc * (virtual_ChargeThroughput + doc*qcell)**self.__C_QLOSS - qloss)

        self.__capacity_loss_cyclic += capacity_loss  # pu
        self.__capacity_loss = capacity_loss * self._cell.get_nominal_capacity()  # Ah

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        doc: float = self.__cycle_detector.get_depth_of_cycle() # DOC

        rinc_cyclic: float = self.__rinc_cyclic
        k_ri_cyclic = self.get_stressfkt_ri_cyc(doc)
        if k_ri_cyclic == 0.0:
            virtual_ChargeThroughput: float = 0
        else:
            virtual_ChargeThroughput: float = (rinc_cyclic / k_ri_cyclic)**(1 / self.__A_RINC)

        qcell: float = battery_state.capacity / battery_state.nominal_voltage / self._cell.get_parallel_scale()
        # single cell capacity in Ah

        resistance_increase = max(0, k_ri_cyclic * (virtual_ChargeThroughput + doc*qcell)\
                              **self.__A_RINC - self.__rinc_cyclic)


        self.__rinc_cyclic += resistance_increase
        self.__resistance_increase = resistance_increase  # pu

    def get_stressfkt_ca_cyc(self, doc: float) -> float:
        """
        get the stress factor for cyclic aging capacity loss

        Parameters
        ----------
        doc : depth of cycle

        Returns
        -------
        float : stress parameters of cyclic aging (capacity loss)

        """
        doc = self.__check_doc_range(doc)
        return float(self.__capacity_cyc_interp1d(doc))

    def get_stressfkt_ri_cyc(self, doc: float) -> float:
        """
        get the stress factor for cyclic aging resistance increase

        Parameters
        ----------
        doc : depth of cycle

        Returns
        -------
        float : stress parameters of cyclic aging (resistance increase)

        """
        doc = self.__check_doc_range(doc)
        return float(self.__ri_cyc_interp1d(doc))

    def __check_doc_range(self, doc: float) -> float:
        if doc < 0.0:
            self.__log.warn(str(doc) + ' is out of interpolation range')
            return 0.0
        elif doc > 1.0:
            self.__log.warn(str(doc) + ' is out of interpolation range')
            return 1.0
        else:
            return doc

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
        self.__capacity_loss_cyclic = 0
        self.__rinc_cyclic = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        self.__log.close()
