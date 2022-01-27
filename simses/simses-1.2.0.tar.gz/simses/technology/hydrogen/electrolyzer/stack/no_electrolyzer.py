from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel


class NoElectrolyzer(ElectrolyzerStackModel):

    def __init__(self):
        super(NoElectrolyzer, self).__init__()

    def calculate(self, power: float, state: ElectrolyzerState) -> None:
        pass

    def get_reference_voltage_eol(self, resistance_increase: float, exchange_currentdensity_decrease: float) -> float:
        return 0

    def get_current(self):
        return 0

    def get_current_density(self):
        return 0

    def get_voltage(self):
        return 2

    def get_hydrogen_production(self):
        return 0

    def get_oxygen_production(self):
        return 0

    def get_water_use(self):
        return 0

    def get_number_cells(self):
        return 0

    def get_geom_area_stack(self):
        return 0

    def get_nominal_stack_power(self):
        return 0

    def get_heat_capacity_stack(self):
        return 0

    def get_partial_pressure_h2(self):
        return 0

    def get_partial_pressure_o2(self):
        return 0

    def get_sat_pressure_h2o(self):
        return 0

    def get_water_in_stack(self):
        return 0

    def get_nominal_current_density(self):
        return 0

    def get_thermal_resistance_stack(self):
        return 0

    def close(self):
        pass
