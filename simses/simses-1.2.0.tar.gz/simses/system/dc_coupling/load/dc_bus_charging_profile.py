from simses.commons.profile.file import FileProfile
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.dc_coupling.load.dc_load import DcLoad


class DcBusChargingProfile(DcLoad):

    """
    DcBusChargingProfile is able to read in SOC profiles and calculates a load power for charging.
    """

    def __init__(self, config: GeneralSimulationConfig, capacity: float, file_name: str):
        super().__init__()
        self.__profile: FileProfile = FileProfile(config, file_name, value_index=2)
        self.__power: float = 0.0
        self.__capacity: float = capacity
        self.__last_soc: float = self.__profile.next(config.start)
        self.__timestep: float = config.timestep
        self.__Wh_to_Ws: float = 3600.0
        self.__charge_efficiency: float = 0.98

    def get_power(self) -> float:
        return self.__power

    def calculate_power(self, time: float) -> None:
        soc = self.__profile.next(time)
        power = (soc - self.__last_soc) * self.__capacity * self.__Wh_to_Ws / self.__timestep / self.__charge_efficiency
        self.__power = max(power, 0.0)
        self.__last_soc = soc

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def close(self) -> None:
        pass
