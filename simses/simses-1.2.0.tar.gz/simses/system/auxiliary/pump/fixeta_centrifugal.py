from simses.commons.log import Logger
from simses.system.auxiliary.pump.abstract_pump import Pump


class FixEtaCentrifugalPump(Pump):
    """FixEtaCentrifugalPump is a pump with a constant efficiency."""

    def __init__(self, efficiency: float):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__eta_pump = efficiency  # pump efficiency p.u.
        if self.__eta_pump <= 0 or self.__eta_pump > 1:
            self.__log.error('Pump efficiency has to be greater than 0 and smaller or equal to 1. It is set to 1.')
            self.__eta_pump = 1
        self.__power = 0.0

    def calculate_pump_power(self, pressure_loss: float) -> None:
        if pressure_loss < 0:
            self.__log.error('Pressure losses are negative. Check sign of pressure drop and flow rate.')
        self.__power = pressure_loss / self.__eta_pump

    def set_eta_pump(self, flow_rate, flow_rate_max, flow_rate_min) -> None:
        pass

    def get_pump_power(self) -> float:
        return self.__power

    def close(self):
        super().close()
        self.__log.close()
