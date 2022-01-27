from simses.system.auxiliary.heating_ventilation_air_conditioning.hvac import HeatingVentilationAirConditioning


class NoHeatingVentilationAirConditioning(HeatingVentilationAirConditioning):

    def __init__(self):
        super().__init__()

    def run_air_conditioning(self, temperature_time_series: [float], temperature_timestep: float, ambient_air_temperature: float) -> float:
        pass

    def get_electric_power(self) -> float:
        return 0

    def get_max_thermal_power(self) -> float:
        return 0

    def get_set_point_temperature(self) -> float:
        return 298.15

    def get_thermal_power(self) -> float:
        return 0

    def get_cop(self) -> float:
        return 1.0

    def get_scop(self) -> float:
        return 1.0

    def get_seer(self) -> float:
        return 1.0

    def get_temperature_dead_band(self) -> float:
        return 0.0

    def update_air_parameters(self, air_mass: float = None, air_specific_heat: float = None, air_density: float = None) -> None:
        pass

    def set_electric_power(self, electric_power: float) -> None:
        """Used in cases where multiple runs of the HVAC take place within a SimSES timestep"""
        pass
