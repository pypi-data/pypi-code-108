import warnings
import numpy
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.system import SystemState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.system.thermal.ambient.location_temperature import LocationAmbientTemperature
from simses.system.thermal.model.system_thermal_model import SystemThermalModel


class NoSystemThermalModel(SystemThermalModel):
    """This model does nothing - keeps the system air temperature equal to ambient temperature"""

    LARGE_NUMBER = numpy.finfo(numpy.float64).max * 1e-100

    def __init__(self, ambient_thermal_model: AmbientThermalModel, general_config: GeneralSimulationConfig):
        super().__init__()
        self.start_time = general_config.start
        if isinstance(ambient_thermal_model, LocationAmbientTemperature):
            warnings.warn('LocationAmbientTemperature is chosen with NoSystemThermalModel.\n'
                  'StorageTechnology temperatures will be initialized and will not be updated further.\n'
                  'Please Select ConstantAmbientTemperature if this is not desired.\n')
        self.__ambient_thermal_model = ambient_thermal_model
        self.__system_temperature = self.__ambient_thermal_model.get_initial_temperature()  # K
        self.__air_specific_heat = 1006  # J/kgK, cp (at constant pressure)
        # this is the internal air temperature within the container. Initialized with ambient temperature

    def calculate_temperature(self, time, state: SystemState, states: [SystemState]):
        self.__system_temperature = self.__ambient_thermal_model.get_temperature(time)

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def get_temperature(self):
        return self.__system_temperature

    def get_ambient_temperature(self) -> float:
        return self.__system_temperature

    def get_solar_irradiation_thermal_load(self) -> float:
        return 0.0

    def get_hvac_thermal_power(self) -> float:
        return 0.0

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        pass

    def update_air_parameters(self):
        pass
