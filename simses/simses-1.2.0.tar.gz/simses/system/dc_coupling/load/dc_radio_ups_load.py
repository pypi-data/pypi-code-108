from datetime import datetime

from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.dc_coupling.load.dc_load import DcLoad


class DCRadioUPSLoad(DcLoad):

    """
    DcBusChargingFixed acts as fixed load profile for bus connecting to the storage system at the same time each day.
    """

    def __init__(self, charging_power: float):
        super().__init__()
        self.__Load_by_Night: float = charging_power  # W
        self.__Load: float = 800.0

    def get_power(self) -> float:
        return self.__Load

    def calculate_power(self, time: float) -> None:
        tstmp = datetime.utcfromtimestamp(time)
        hour = tstmp.hour + tstmp.minute / 60. + tstmp.second / 3600.
        if 20 <= hour <= 24:
            self.__Load = self.__Load_by_Night
        elif 0 <= hour <= 8:
            self.__Load = self.__Load_by_Night
        else:
            self.__Load = 800.0


    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def close(self) -> None:
        pass