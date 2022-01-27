from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig
from simses.commons.log import Logger
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.efficiency_curves import \
    PemElectrolyzerEfficiencyCurves
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.electrical_model import \
    PemElectricalModel
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.fluid_model import \
    PemFluidModel
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.membrane_model import \
    PemMembraneModel
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.parameters import \
    ParametersPemElectrolyzerMultiDimAnalytic
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.pressure_model import \
    PemPressureModel
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel


class PemElectrolyzerMultiDimAnalytic(ElectrolyzerStackModel):
    """An PEM-Electrolyzer is a special typ of an Electrolyzer"""

    # TODO Are those variables the same for every PemElectrolyzerMultiDimAnalytic?

    __NOM_POWER_CELL = 5000  # W   side length = 35 cm
    __MAX_POWER_CELL = 7962.5  # W  based on polarizationscurve model from: PEM-Elektrolyse-Systeme zur Anwendung in Power-to-Gas Anlagen
    __RATIO_NOM_TO_MAX = __NOM_POWER_CELL / __MAX_POWER_CELL

    __NOMINAL_CURRENT_DENSITY = 2  # A/cm²
    __MAX_CURRENTDENSITY_CELL = 3  # A/cm2
    __NOM_CURRENTDENSITY_CELL = 2  # A/cm²
    __MIN_CURRENTDENSITY_CELL = 0  # A/cm2
    __NOM_VOLTAGE_CELL = 2  # V

    __HEAT_CAPACITY = 0.448  #  J/K/W for >= 50 kW from: Maximilian Möckl ZAE
    __WATER_POWER_DENSITY = 0.025  # kg / kW from: Maximilian Möckl ZAE

    def __init__(self, electrolyzer_maximal_power: float, electrolyzer_data_config: ElectrolyzerDataConfig):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__number_cells: float = max(round(electrolyzer_maximal_power / self.__MAX_POWER_CELL), 1)
        self.__max_stack_power: float = self.__number_cells * self.__MAX_POWER_CELL  # W
        self.__nominal_stack_power: float = self.__RATIO_NOM_TO_MAX * self.__max_stack_power  # W
        self.__heat_capacity_stack: float = self.__HEAT_CAPACITY * self.__nominal_stack_power  # J/K
        self.__water_in_stack: float = self.__WATER_POWER_DENSITY * self.__nominal_stack_power / 1000.0  # 0.125 kg/kW
        self.__log.info('maximal stack power of electrolyzer was adapted to: ' + str(self.__max_stack_power))
        self.__log.info('nominal stack power of electrolyzer is: ' + str(self.__nominal_stack_power))
        self.__log.info('number of serial cells is: ' + str(self.__number_cells))
        # initialize models
        self.__parameters = ParametersPemElectrolyzerMultiDimAnalytic(electrolyzer_data_config)
        self.__pressure_model: PemPressureModel = PemPressureModel(self.__parameters)
        self.__membrane_model: PemMembraneModel = PemMembraneModel(self.__pressure_model)
        self.__electrical_model: PemElectricalModel = PemElectricalModel(self.__membrane_model, self.__pressure_model,
                                                                         self.__parameters)
        self.__fluid_model: PemFluidModel = PemFluidModel(self.__membrane_model)
        self.__efficiency_curve_calculation = PemElectrolyzerEfficiencyCurves(self.__electrical_model,
                                                                              self.__membrane_model,
                                                                              self.__pressure_model, self.__fluid_model)
        # initialize variables
        self.__voltage_stack: float = 0.0
        self.__current_stack: float = 0.0
        self.__current_cell: float = 0.0
        self.__h2o_use_stack: float = 0.0
        self.__o2_generation_stack: float = 0.0
        self.__h2_generation_stack: float = 0.0
        self.__part_pressure_h2: float = 0.0
        self.__part_pressure_o2: float = 0.0
        self.__sat_pressure_h2o: float = 0.0

    def calculate(self, power: float, state: ElectrolyzerState):
        # calculation of current, partial pressures and cell voltage at cell level
        power_density: float = power / self.__number_cells / self.__membrane_model.get_geometric_area_cell()  # W/cm2
        # calculation of current and voltage at stack level
        current_dens_cell = self.__electrical_model.get_current_density(power_density, state)  # A/cm2
        voltage_cell = self.__electrical_model.get_cell_voltage(current_dens_cell, state)  # V
        self.__current_stack = current_dens_cell * self.__membrane_model.get_geometric_area_cell()  # A  cells are serial connected to a Stack
        self.__current_cell = self.__current_stack
        self.__voltage_stack = voltage_cell * self.__number_cells  # V  cells are serial connected to one stack
        # calculation of pressures
        self.__part_pressure_h2 = self.__pressure_model.get_partial_pressure_h2(state, current_dens_cell)
        self.__part_pressure_o2 = self.__pressure_model.get_partial_pressure_o2(state, current_dens_cell)
        self.__sat_pressure_h2o = self.__pressure_model.get_sat_pressure_h2o(state.temperature)
        # net use of water, production of hydrogen and oxygen at Stack level
        h2_net_cathode = self.__fluid_model.get_h2_net_cathode(state, self.__current_cell)  # mol/s
        o2_net_anode = self.__fluid_model.get_o2_net_anode(state, self.__current_cell)  # mol/s
        h2o_net_use_cell: float = self.__fluid_model.get_h2o_net_use_cell(state, self.__current_cell)
        self.__h2o_use_stack = h2o_net_use_cell * self.__number_cells  # mol/s
        self.__o2_generation_stack = o2_net_anode * self.__number_cells  # mol/s
        self.__h2_generation_stack = h2_net_cathode * self.__number_cells  # mol/s

    def get_nominal_current_density(self):
        return self.__NOMINAL_CURRENT_DENSITY

    def get_reference_voltage_eol(self, resistance_increase, exchange_current_decrease) -> float:
        """
        return cell voltage of electrolyzer at 2 A/cm², p_anode = 0 barg, p_cathode = 0 barg and temperature = 80°C
        this cell voltage is needed for the calculation of the SOH of the electrolyzer
        :return: cell voltage in V
        """
        # TODO implement function
        # return self.calculate_cell_voltage(30, 0, 0, 2, resistance_increase, exchange_current_decrease)
        ref_electrolyzer_state = ElectrolyzerState(1, 1)
        ref_electrolyzer_state.temperature = 80  # °C
        ref_electrolyzer_state.pressure_cathode = 30  # barg
        ref_electrolyzer_state.pressure_anode = 0  # barg
        ref_electrolyzer_state.exchange_current_decrease = exchange_current_decrease
        ref_electrolyzer_state.resistance_increase = resistance_increase
        current_dens_ref = 2  # A/cm²
        return self.__electrical_model.get_cell_voltage(current_dens_ref, ref_electrolyzer_state)

    def get_current(self):
        return self.__current_stack

    def get_current_density(self):
        return self.__current_stack / self.__membrane_model.get_geometric_area_cell()

    def get_hydrogen_production(self):
        return self.__h2_generation_stack

    def get_oxygen_production(self):
        return self.__o2_generation_stack

    def get_voltage(self):
        return self.__voltage_stack

    def get_water_use(self):
        return self.__h2o_use_stack

    def get_number_cells(self):
        return self.__number_cells

    def get_geom_area_stack(self):
        return self.__number_cells * self.__membrane_model.get_geometric_area_cell()

    def get_nominal_stack_power(self):
        return self.__nominal_stack_power

    def get_heat_capacity_stack(self):
        return self.__heat_capacity_stack

    def get_water_in_stack(self):
        return self.__water_in_stack

    def get_partial_pressure_h2(self):
        return self.__part_pressure_h2

    def get_partial_pressure_o2(self):
        return self.__part_pressure_o2

    def get_sat_pressure_h2o(self):
        return self.__sat_pressure_h2o

    def get_efficiency_curve(self, hydrogen_state: ElectrolyzerState):
        return self.__efficiency_curve_calculation.calculate_efficiency_curves(hydrogen_state)

    def close(self):
        self.__log.close()

    def get_thermal_resistance_stack(self):
        pass
