from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.file import FileProfile
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.commons.config.simulation.profile import ProfileConfig


class LocationAmbientTemperature(AmbientThermalModel):

    """
    LocationAmbientTemperature provides a ambient temperature profile for a specified location.
    Ambient temperature time series data for Berlin, Germany and Jodhpur, India from DLR Greenius Tool:
    https://www.dlr.de/sf/en/desktopdefault.aspx/tabid-11688/20442_read-44865/
    """

    def __init__(self, profile_config: ProfileConfig, general_config: GeneralSimulationConfig):
        super().__init__()
        self.__start_time = general_config.start
        self.__file = FileProfile(general_config, profile_config.ambient_temperature_profile_file)
        self.__profile_config: ProfileConfig = profile_config
        self.__general_config: GeneralSimulationConfig = general_config

    def get_temperature(self, time) -> float:
        temp_c = self.__file.next(time)  # in °C
        temp_k = temp_c + 273.15  # in K
        return temp_k

    def get_initial_temperature(self) -> float:
        return self.get_temperature(self.__start_time)  # in K

    def create_instance(self) -> AmbientThermalModel:
        """
        reinstantiates the AmbientThermalModel
        :return: AmbientThermalModel
        """
        return LocationAmbientTemperature(self.__profile_config, self.__general_config)

    def close(self):
        self.__file.close()


