from datetime import datetime
from random import Random

from pytz import timezone

from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.dc_coupling.load.dc_load import DcLoad


class DcBusChargingRandom(DcLoad):

    """
    DcBusChargingRandom acts as load profile for busses connected to the storage system at varying start and end
    times of each day.
    """

    __number_charging_stations: int = 0

    __START_CHARGE_HOUR_MEAN: float = 19.0
    __CHARGE_HOUR_VARIATION: float = 3.0

    __DURATION_CHARGE_MEAN: float = 3.0
    __CHARGE_DURATION_VARIATION: float = 1.0

    __UTC: timezone = timezone('UTC')

    def __init__(self, charging_power: float):
        super().__init__()
        self.__CHARGE_POWER: float = charging_power  # W
        self.__class__.__number_charging_stations += 1
        self.__random: Random = Random(3515723 * self.__class__.__number_charging_stations)
        self.__start_charge: float = 0.0
        self.__stop_charge: float = 0.0
        self.__day: int = 0
        self.__power: float = 0.0
        self.__charge_active: bool = False

    def __get_start_charging(self, date: datetime) -> float:
        tstmp: float = self.__random.uniform(self.__START_CHARGE_HOUR_MEAN - self.__CHARGE_HOUR_VARIATION,
                                     self.__START_CHARGE_HOUR_MEAN + self.__CHARGE_HOUR_VARIATION) * 3600.0
        minutes, seconds = divmod(tstmp, 60.0)
        hour, minutes = divmod(minutes, 60.0)
        date = date.replace(hour=int(hour), minute=int(minutes), second=int(seconds))
        return self.__UTC.localize(date).timestamp()

    def __get_charging_duration(self) -> float:
        return self.__random.uniform(self.__DURATION_CHARGE_MEAN - self.__CHARGE_DURATION_VARIATION,
                                     self.__DURATION_CHARGE_MEAN + self.__CHARGE_DURATION_VARIATION) * 3600.0

    def __set_charging_times(self, time: float) -> None:
        date = datetime.utcfromtimestamp(time)
        if self.__day != date.day and not self.__charge_active:
            self.__day = date.day
            self.__start_charge = self.__get_start_charging(date)
            self.__stop_charge = self.__start_charge + self.__get_charging_duration()

    def get_power(self) -> float:
        return self.__power

    def calculate_power(self, time: float) -> None:
        self.__set_charging_times(time)
        # hour = tstmp.hour + tstmp.minute / 60. + tstmp.second / 3600.
        if self.__start_charge < time < self.__stop_charge:
            self.__power = self.__CHARGE_POWER
            self.__charge_active = True
        else:
            self.__power = 0.0
            self.__charge_active = False

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def close(self) -> None:
        pass
