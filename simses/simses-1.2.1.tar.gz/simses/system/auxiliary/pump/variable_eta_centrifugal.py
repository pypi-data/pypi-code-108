import pandas as pd
import scipy.interpolate

from simses.commons.log import Logger
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.commons.config.data.auxiliary import AuxiliaryDataConfig


class VariableEtaCentrifugalPump(Pump):
    """VariableEtaCentrifugalPump is a pump with an efficiency dependent on the flow rate."""

    def __init__(self, auxiliary_data_config: AuxiliaryDataConfig):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__power = 0
        self.__eta = 0
        self.__ETA_FILE = auxiliary_data_config.pump_eta_file
        self.__efficiency = pd.read_csv(self.__ETA_FILE, header=None, index_col=0)
        self.__flow_rate_arr = self.__efficiency.iloc[0] * 10 ** -3 / 60  # m^3/s
        self.__eta_arr = self.__efficiency.iloc[1]/100
        self.__efficiency_interp1d = scipy.interpolate.interp1d(self.__flow_rate_arr, self.__eta_arr, kind='linear')
        self.__max_pump_flow_rate = max(self.__flow_rate_arr)
        self.__min_pump_flow_rate = min(self.__flow_rate_arr)

    def calculate_pump_power(self, pressure_loss) -> None:
        if pressure_loss < 0:
            self.__log.error('Pressure losses are negative. Check sign of pressure drop and flow rate.')
        self.__power = pressure_loss / self.__eta

    def set_eta_pump(self, flow_rate, flow_rate_max, flow_rate_min) -> None:
        self.__log.debug('Flow rate is ' + str(flow_rate))
        if self.__min_pump_flow_rate > flow_rate > self.__max_pump_flow_rate:
            self.__log.error('Flow rate is to high or low for the pump. Use different pump data. '
                             'Pump efficiency is set to 1.')
            self.__eta = 1
        elif flow_rate == 0:
            self.__eta = 1
        else:
            self.__eta = self.__efficiency_interp1d(flow_rate)

        if self.__eta < 0 or self.__eta > 1:
            self.__log.error('Pump efficiency has to be greater than 0 and smaller or equal to 1. It is set to 1.')
            self.__eta = 1
        self.__log.debug('Pump Efficiency is ' + str(self.__eta))

    def get_pump_power(self) -> float:
        return self.__power

    def close(self):
        super().close()
        self.__log.close()
