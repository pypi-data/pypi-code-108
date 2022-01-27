from simses.commons.config.simulation.electrolyzer import ElectrolyzerConfig
from simses.commons.constants import Hydrogen
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.system.auxiliary.water_heating.water_heater import WaterHeating
from simses.technology.hydrogen.control.thermal.ideal_var_flow import \
    IdealVarFlowThermalController
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel
from simses.technology.hydrogen.electrolyzer.thermal.abstract_model import ThermalModel


class SimpleThermalModel(ThermalModel):
    """ This model functions at Electrolyzer Level.
    This model calculates the temperaturechange in the electrlyzer stack
    the elelctrolyzer is represented by a area element"""

    def __init__(self, electrolyzer: ElectrolyzerStackModel, water_heating: WaterHeating, pump: Pump,
                 temperature: float, config: ElectrolyzerConfig):
        super().__init__()
        self.__HEAT_CAPACITY = electrolyzer.get_heat_capacity_stack() # J/K
        nominal_stack_power = electrolyzer.get_nominal_stack_power()  # W
        self.__max_water_flow_stack = self.__calculate_max_water_flow_stack(nominal_stack_power)  # mol/s
        self.__min_water_flow_stack = 0.1 * self.__max_water_flow_stack  # mol/s
        self.__thermal_controller = IdealVarFlowThermalController(config, self.__HEAT_CAPACITY)
        self.__temperature_stack_1 = 0  # °C
        self.__NUMBER_CELLS = electrolyzer.get_number_cells()
        self.__GEOM_AREA_STACK = electrolyzer.get_geom_area_stack() # cm²
        self.__GEOM_AREA_CELL = self.__GEOM_AREA_STACK / self.__NUMBER_CELLS  # cm²
        self.__convection_heat = 0  # initialize variable
        self.__heat_generation = 0  # initialize variable
        self.__heat_vape = 0  # initialize variable
        self.__TH_NEUT_VOLTAGE = 286 * 10 ** 3 / (2 * Hydrogen.FARADAY_CONST)  # V
        self.__SURFACE_RATIO_FRAME = self.__calculate_surface_ratio_frame(nominal_stack_power)
        self.__SURFACE_RATIO_ENDPLATE = self.__calculate_surface_ratio_endplates(nominal_stack_power)
        self.__SURFACE_RADTIO_TUBES = self.__calculate_surface_ratio_tubes(nominal_stack_power)
        self.__SURFACE_RATIO_SEPARATOR = self.__calculate_surface_ratio_separator(nominal_stack_power)
        self.__HEAT_TRANSMISSION_COEF_TUBES = self.__calculate_heat_transmission_coef_tubes(nominal_stack_power)
        self.__AMOUNT_WATER = electrolyzer.get_water_in_stack() # kg
        self.__h2o_flow_stack = 0  # mol/s
        self.__heat_h2o = 0  #
        self.__pump = pump
        self.__pump_power = 0  # W
        self.__tube_pressure_loss = 0  # bar
        self.__water_heating = water_heating
        self.__ambient_temperature: float = temperature - 273.15  # C

    def calculate(self, time: float, state: ElectrolyzerState, pressure_cathode_0, pressure_anode_0) -> None:
        timestep = time - state.time
        temperature_stack_0 = state.temperature  # °C
        current_dens = state.current / self.__GEOM_AREA_CELL # A/cm²
        sat_p_h2o = state.sat_pressure_h2o  # bar
        h2_genearation_per_area = state.hydrogen_production / self.__GEOM_AREA_STACK  # mol/s/cm²
        o2_generation_per_area = state.oxygen_production / self.__GEOM_AREA_STACK  # mol/s/cm²
        h2o_use_per_area = state.water_use / self.__GEOM_AREA_STACK  # mol/s/cm²

        # water gives all its heatenergy to the stack
        temperature_h2o_out = temperature_stack_0  # °C

        # specific heat generation in electrolyseur cell
        spec_heat_cell = self.__calculate_spec_heat_cell(state.voltage, current_dens, temperature_stack_0,
                                                         h2_genearation_per_area, o2_generation_per_area,
                                                         pressure_cathode_0, pressure_anode_0, sat_p_h2o)

        # specific heat dissipation through frame, endplates, tubes and gas separator
        spec_heat_frame = self.__calculate_spec_heat_frame(temperature_stack_0, self.__ambient_temperature) # W/cm²
        spec_heat_endplates = self.__calculate_spec_heat_endplate(temperature_stack_0, self.__ambient_temperature)  # W/cm²
        spec_heat_tubes = self.__calculate_spec_heat_tubes(temperature_stack_0, self.__ambient_temperature)  # W/cm 2
        spec_heat_separator = self.__calculate_spec_heat_separator(temperature_stack_0, self.__ambient_temperature)

        # specific heat sink because of freshwater
        spec_heat_fresh_water = self.__calculate_spec_heat_freshwater(h2o_use_per_area, temperature_h2o_out,
                                                                      self.__ambient_temperature)

        # total heat generation electrolyzer stack
        heat_stack = (spec_heat_cell - spec_heat_frame - 2 * spec_heat_endplates - spec_heat_tubes - spec_heat_separator
                      - spec_heat_fresh_water) * self.__GEOM_AREA_STACK # W

        # calculation of watertemperature and waterflow for tempering the stack
        self.__thermal_controller.calculate(temperature_stack_0, heat_stack, timestep, current_dens)
        temperature_h2o_in = temperature_stack_0 + self.__thermal_controller.get_delta_water_temp_in()  # °C
        self.__h2o_flow_stack = self.__thermal_controller.get_h2o_flow()  # mol/s
        self.__heat_h2o = self.__calculate_heat_h2o(self.__h2o_flow_stack, temperature_h2o_in, temperature_h2o_out)

        # self.__temperature_stack_1 = temperature_stack_0 + timestep / self.__HEAT_CAPACITY * (
        #             heat_stack + self.__heat_h2o) + 273.15  # K -> °C
        # temperature calculation stack
        if self.__thermal_controller.get_heat_control_on():
            self.__temperature_stack_1 = temperature_stack_0 + timestep / self.__HEAT_CAPACITY * (heat_stack + self.__heat_h2o)  # °C
            # if heat control is on, water is circulated through the stack and controls the temperature of the stack
            # with its own temperature-> heat capacity of water is not accounted
        else:
            self.__temperature_stack_1 = temperature_stack_0 + timestep / (self.__HEAT_CAPACITY + self.__AMOUNT_WATER *
                                                                           Hydrogen.HEAT_CAPACITY_WATER) * \
                                         (heat_stack + self.__heat_h2o)  # °C
            # if heat control is off there is no water circulation -> heat capacity of water which remains in the stack
            # needs to be accounted for the cooling process

        # convection heat: heat that is transported to the ambient area
        if self.__heat_h2o < 0:
            self.__convection_heat = (spec_heat_frame + spec_heat_endplates + spec_heat_tubes + spec_heat_separator) * \
                                     self.__GEOM_AREA_STACK * self.__NUMBER_CELLS - self.__heat_h2o
        else:
            self.__convection_heat = (spec_heat_frame + spec_heat_endplates + spec_heat_tubes + spec_heat_separator) * \
                                     self.__GEOM_AREA_STACK * self.__NUMBER_CELLS

    def __calculate_spec_heat_freshwater(self, h2o_use_per_area, temp_h2o_in, temp_ambient) -> float:
        """ calculates the cooling effect of the feedwater
        if temp_h2o_in > temp_ambient: feedwater cools the water in the circulation"""
        delta_temp = temp_ambient - temp_h2o_in
        return Hydrogen.HEAT_CAPACITY_WATER * h2o_use_per_area * Hydrogen.MOLAR_MASS_WATER * delta_temp

    def __calculate_spec_heat_frame(self, temp_stack, temp_abient) -> float:
        delta_temp = temp_stack - temp_abient
        k_frame = 2.5  # W/(m² K)
        return k_frame * self.__SURFACE_RATIO_FRAME * delta_temp  # W/cm²

    def __calculate_spec_heat_endplate(self, temp_stack, temp_ambient) -> float:
        delta_temp = temp_stack - temp_ambient
        k_endplate = 3.6  # # W/(m² K)
        return k_endplate * self.__SURFACE_RATIO_ENDPLATE * delta_temp  # W/cm²

    def __calculate_spec_heat_tubes(self, temp_stack, temp_ambient) -> float:
        delta_temp = temp_stack - temp_ambient
        return self.__HEAT_TRANSMISSION_COEF_TUBES * self.__SURFACE_RADTIO_TUBES * delta_temp  # W/cm²

    def __calculate_spec_heat_separator(self, temp_stack, temp_ambient) -> float:
        delta_temp = temp_stack - temp_ambient
        k_separator = 9  # W/(m² K)
        return k_separator * self.__SURFACE_RATIO_SEPARATOR * delta_temp

    def __calculate_heat_h2o(self, h2o_flow_stack, temp_h2o_in, temp_h2o_out) -> float:
        delta_temp = temp_h2o_in - temp_h2o_out
        self.__water_heating.calculate_heating_power(h2o_flow_stack, delta_temp)
        return self.__water_heating.get_heating_power()

    def __calculate_spec_heat_generation_cell(self, cell_voltage, current_dens) -> float:
        return (cell_voltage / self.__NUMBER_CELLS - self.__TH_NEUT_VOLTAGE) * current_dens

    def __calcutlate_spec_heat_vape_h2o(self, temp_stack, h2_gen_per_area, o2_gen_per_area, p_c_0, p_a_0,
                                        sat_p_h2o) -> float:
        if h2_gen_per_area > 0:
            h2o_steam_flow_per_area = (sat_p_h2o / (1 + p_c_0 - sat_p_h2o)) * h2_gen_per_area + (sat_p_h2o /
                                                (1 + p_a_0 - sat_p_h2o)) * o2_gen_per_area  # mol/s/cm²
        else:
            h2o_steam_flow_per_area = 0
        return - (-43.79 * temp_stack + 4.509 * 10 ** 4) * h2o_steam_flow_per_area  # W/cm²

    def __calculate_spec_heat_cell(self, cell_voltage, current_dens, temp_stack, h2_gen_per_area, o2_gen_per_area,
                                   p_c_0, p_a_0, sat_p_h2o) -> float:
        spec_heat_vape_h2o = self.__calcutlate_spec_heat_vape_h2o(temp_stack, h2_gen_per_area, o2_gen_per_area, p_c_0,
                                                                  p_a_0, sat_p_h2o)
        spec_heat_gen_cell = self.__calculate_spec_heat_generation_cell(cell_voltage, current_dens)
        return spec_heat_gen_cell + spec_heat_vape_h2o

    def __calculate_surface_ratio_frame(self, nominal_stack_power) -> float:
        m_frame = -591 / 5750  # 1/kW
        c_frame = 357.1
        return (m_frame * nominal_stack_power / 1000 + c_frame) * 10 ** (-7)  # m²/cm²

    def __calculate_surface_ratio_endplates(self, nominal_stack_power) -> float:
        m_endplate = -129 / 11500  # 1/kW
        c_endplate = 19
        return (m_endplate * nominal_stack_power / 1000 + c_endplate) * 10 ** (-7)  # m²/cm²

    def __calculate_surface_ratio_tubes(self, nominal_stack_power) -> float:
        m_tubes = -107 / 115000  # 1/kW
        c_tubes = 2.06
        return (m_tubes * nominal_stack_power / 1000 + c_tubes) * 10 ** (-5)  # m²/cm²

    def __calculate_heat_transmission_coef_tubes(self, nominal_stack_power) -> float:
        m_tubes = 53 / 115000  # 1/kW
        c_tubes = 0.4
        return m_tubes * nominal_stack_power / 1000 + c_tubes  # W/m²/K

    def __calculate_surface_ratio_separator(self, nominal_stack_power) -> float:
        m_separator = -329 / 57500  # 1/kW
        c_separator = 8.52
        return (m_separator * nominal_stack_power / 1000 + c_separator)  * 10 ** (-6)  # m²/cm²

    def __calculate_max_water_flow_stack(self, electrolyzer_nominal_power):
        """ calculates max water flow the cooling pump can provide in dependency of nominal power of electrolyzer
        based on data from thesis: PEM-Elektrolyse-Systeme zur Anwendung in Power-to-Gas Anlagen"""
        # max water flow rate = 1.5 kg/s for a 1250 kW EL-Stack
        water_flow_rate = 11.9 / 1250  # 11.9 kg/s / 1250 kW
        el_nom_power_kW = electrolyzer_nominal_power / 1000  # W -> kW
        return water_flow_rate * el_nom_power_kW / Hydrogen.MOLAR_MASS_WATER  # mol/s

    def calculate_pump_power(self, water_flow_stack) -> None:
        relative_flow = water_flow_stack / self.__max_water_flow_stack
        pressure_loss = 1.985 * 10 ** (-4) * (relative_flow * 100) ** 2 * 10 ** (5) # N/m²
        volume_flow = water_flow_stack * Hydrogen.MOLAR_MASS_WATER / Hydrogen.DENSITY_WATER  # m³/s
        self.__pump.calculate_pump_power(volume_flow * pressure_loss)  # W
        self.__pump_power = self.__pump.get_pump_power()

    def get_temperature(self) -> float:
        return self.__temperature_stack_1

    def get_water_flow_stack(self) -> float:
        return self.__h2o_flow_stack

    def get_power_water_heating(self) -> float:
        return self.__heat_h2o

    def get_pump_power(self) -> float:
        return self.__pump_power

    def get_convection_heat(self) -> float:
        return self.__convection_heat
