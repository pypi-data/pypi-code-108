from abc import abstractmethod, ABC
from simses.commons.state.abstract_state import State
from simses.system.auxiliary.auxiliary import Auxiliary


class SystemThermalModel(ABC):
    """Thermal model of a storage system"""

    def __init__(self):
        # Air parameters
        self.air_pressure = 1 * 10 ** 5  # Pa, change if container is pressurized
        self.universal_gas_constant = 8.314  # J/kgK
        self.molecular_weight_air = 28.965 * 10 ** -3  # kg/mol

    @abstractmethod
    def get_temperature(self) -> float:
        """
        Returns the current temperature of the system (Internal air temperature)

        Parameters
        -------

        Returns
        -------
        float
            system temperature in Kelvin
        """

        pass

    @abstractmethod
    def get_ambient_temperature(self) -> float:
        """
        Returns the ambient temperature at the location
        """

        pass

    @abstractmethod
    def get_solar_irradiation_thermal_load(self) -> float:
        """
        returns the solar irradiation thermal load on the container in W
        """
        pass

    @abstractmethod
    def get_hvac_thermal_power(self) -> float:
        """
        returns the total HVAC thermal power in W
        """
        pass

    @abstractmethod
    def get_auxiliaries(self) -> [Auxiliary]:
        pass

    @abstractmethod
    def update_air_parameters(self):
        pass

    @abstractmethod
    def calculate_temperature(self, time: float, storage_system_ac_state: State, storage_system_dc_states: [State]) -> None:
        """
        Calcualtes the current temperature of the system

        Parameters
        ----------
        time : current simulation time
        state : current system state

        Returns
        -------
        :param time:
        :param storage_system_dc_states:
        :param storage_system_ac_state:

        """
        pass

    @abstractmethod
    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        pass

    def close(self):
        """
        Closing all open resources in system thermal model

        Parameters
        ----------

        Returns
        -------

        """
        pass
