from abc import ABC, abstractmethod
from simses.system.auxiliary.auxiliary import Auxiliary


class HeatingVentilationAirConditioning(Auxiliary, ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    # temperature_timestep: time
    def run_air_conditioning(self, temperature_time_series: [float], temperature_timestep: float, ambient_air_temperature: float) -> None:
        pass

    @abstractmethod
    def get_electric_power(self) -> float:
        pass

    @abstractmethod
    def get_max_thermal_power(self) -> float:
        pass

    @abstractmethod
    def get_thermal_power(self) -> float:
        pass

    @abstractmethod
    def get_set_point_temperature(self) -> float:
        pass

    @abstractmethod
    def get_scop(self) -> float:
        pass

    @abstractmethod
    def get_seer(self) -> float:
        pass

    @abstractmethod
    def get_temperature_dead_band(self) -> float:
        pass

    @abstractmethod
    def update_air_parameters(self, air_mass: float = None, air_specific_heat: float = None, air_density: float = None) -> None:
        pass

    def get_coefficients(self) -> [float, float, float]:
        """
        Needed for plotting BA Hörmann
        """
        pass

    def get_plotting_arrays(self) -> [[float], [float], [float], [float], [float], [float]]:
        """
        Needed for plotting BA Hörmann
        """
        pass

    def ac_operation_losses(self) -> float:
        return self.get_electric_power()

    @abstractmethod
    def set_electric_power(self, electric_power: float) -> None:
        pass
