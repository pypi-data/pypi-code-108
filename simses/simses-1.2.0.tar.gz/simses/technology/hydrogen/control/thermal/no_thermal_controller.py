from simses.technology.hydrogen.control.thermal.thermal_controller import ThermalController


class NoThermalController(ThermalController):

    def __init__(self):
        super().__init__()

    def calculate(self, stack_temperature: float, heat_stack: float, timestep: float, current_dens: float) -> None:
        pass

    def get_heat_control_on(self) -> bool:
        return True

    def get_h2o_flow(self) -> float:
        return 0.0

    def get_delta_water_temp_in(self) -> float:
        return 25.0
