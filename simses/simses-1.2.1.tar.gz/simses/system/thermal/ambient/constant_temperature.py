from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel


class ConstantAmbientTemperature(AmbientThermalModel):

    """
    ConstantAmbientTemperature provides a constant temperature over time.
    """

    def __init__(self, temperature: float = 25):
        """
        Constructor of ConstantAmbientTemperature

        Parameters
        ----------
        temperature :
            temperature in centigrades, default: 25 °C
        """
        super().__init__()
        self.__temperature = 273.15 + temperature  # K

    def get_temperature(self, time) -> float:
        return self.__temperature

    def get_initial_temperature(self) -> float:
        return self.__temperature

    def create_instance(self) -> AmbientThermalModel:
        """
        reinstantiates the AmbientThermalModel
        :return: AmbientThermalModel
        """
        return ConstantAmbientTemperature(self.__temperature)

    def close(self):
        pass
