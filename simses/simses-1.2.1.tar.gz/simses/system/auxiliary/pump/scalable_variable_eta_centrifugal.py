from simses.commons.log import Logger
from simses.system.auxiliary.pump.abstract_pump import Pump


class ScalableVariableEtaCentrifugalPump(Pump):
    """ScalableVariableEtaCentrifugalPump is a pump with an efficiency dependent on the flow rate. The pump is scaled
    based on the maximal and minimal expected flow rate in the system."""

    __ALPHA = 1.082
    __BETA = 1.223

    def __init__(self):
        """
        The efficiency curve of the pump was generated from data from König (2017).
        Literature source: König, Sebastian. "Model-based design and optimization of vanadium redox flow batteries."
        (2017) Karlsruhe Institute of Technology. Dissertation"""
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__power = 0
        self.__eta = 0

    def calculate_pump_power(self, pressure_loss) -> None:
        if pressure_loss == 0:
            self.__power = 0
        else:
            self.__power = pressure_loss / self.__eta

    def set_eta_pump(self, flow_rate, flow_rate_max, flow_rate_min) -> None:
        flow_rate_ratio_max_eff = self.__BETA/(2*self.__ALPHA)
        if (flow_rate_min + flow_rate_max)/(2*flow_rate_max) < flow_rate_ratio_max_eff:
            flow_rate_max_pump = flow_rate_max
        else:
            flow_rate_max_pump = (flow_rate_min + flow_rate_max)/(2*flow_rate_ratio_max_eff)
        flow_rate_ratio = flow_rate/flow_rate_max_pump
        if flow_rate > flow_rate_max_pump:
            self.__log.error('Maximal flow rate for pump is to low. Check maximal flow rate calculation of the system.')
        self.__eta = -self.__ALPHA * flow_rate_ratio ** 2 + self.__BETA * flow_rate_ratio
        if self.__eta < 0 or self.__eta > 1:
            self.__log.error('Pump efficiency has to be greater than 0 and smaller or equal to 1. It is set to 1.')
            self.__eta = 1
        self.__log.debug('Flow rate is ' + str(flow_rate) + '. Pump efficiency is ' + str(self.__eta))

    def get_pump_power(self) -> float:
        return self.__power

    def close(self):
        super().close()
        self.__log.close()
