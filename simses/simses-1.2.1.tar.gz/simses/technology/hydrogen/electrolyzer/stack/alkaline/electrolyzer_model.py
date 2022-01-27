
import numpy as np
import pandas as pd

from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig
from simses.commons.log import Logger
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.alkaline.electrical_model import \
    AlkalineElectricalModel
from simses.technology.hydrogen.electrolyzer.stack.alkaline.fluid_model import \
    AlkalineFluidModel
from simses.technology.hydrogen.electrolyzer.stack.alkaline.parameters import \
    ParametersAlkalineElectrolyzerFit
from simses.technology.hydrogen.electrolyzer.stack.alkaline.pressure_model import \
    AlkalinePressureModel
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel


class AlkalineElectrolyzer(ElectrolyzerStackModel):
    """An Alkaline Electrolyzer is a special type of Electrolyzer"""

    # TODO: Move these Parameters to Config, so it is more easily adjustable?
    __NOM_POWER_CELL = 208  # W
    __MAX_POWER_CELL = 208  # W
    __RATIO_NOM_TO_MAX = __NOM_POWER_CELL / __MAX_POWER_CELL

    __NOMINAL_CURRENT_DENSITY = 0.3  # A/cm²
    __MAX_CURRENTDENSITY_CELL = 0.3  # A/cm2
    __NOM_CURRENTDENSITY_CELL = 0.3  # A/cm²
    # __MIN_CURRENTDENSITY_CELL = 0.03  # A/cm2
    __MIN_CURRENTDENSITY_CELL = 0  # A/cm2
    __NOM_VOLTAGE_CELL = 2  # V

    # TODO Find Alkaline Values!
    # __HEAT_CAPACITY = 0.448           # J/K/W
    __HEAT_CAPACITY = 625000 / 26000    # J/K/W (for 26kW Phoebus Electrolyzer)
    __THERMAL_RESISTANCE = 0.167        # K/W (for 26kW Phoebus Electrolyzer)
    __WATER_POWER_DENSITY = 0.125       # kg / kW from: Maximilian Möckl ZAE

    def __init__(self, electrolyzer_maximal_power: float, electrolyzer_data_config: ElectrolyzerDataConfig):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__number_cells: float = max(round(electrolyzer_maximal_power / self.__MAX_POWER_CELL), 1)
        self.__max_stack_power: float = self.__number_cells * self.__MAX_POWER_CELL  # W
        self.__nominal_stack_power: float = self.__RATIO_NOM_TO_MAX * self.__max_stack_power  # W
        # Scale heat capacity of Phoebus Electrolyser (26kW) to different systems?
        self.__heat_capacity_stack: float = self.__HEAT_CAPACITY * self.__nominal_stack_power  # J/K
        # Scale thermal resistance of Phoebus Electrolyser (26kW) to different systems?
        self.__thermal_resistance_stack: float = self.__THERMAL_RESISTANCE * (26000 / self.__nominal_stack_power)
        self.__water_in_stack: float = self.__WATER_POWER_DENSITY * self.__nominal_stack_power / 1000.0  # 0.125 kg/kW
        self.__log.info('maximal stack power of electrolyzer was adapted to: ' + str(self.__max_stack_power))
        self.__log.info('nominal stack power of electrolyzer is: ' + str(self.__nominal_stack_power))
        self.__log.info('number of serial cells is: ' + str(self.__number_cells))
        # initialize models
        self.__parameters = ParametersAlkalineElectrolyzerFit(electrolyzer_data_config)
        self.__pressure_model: AlkalinePressureModel = AlkalinePressureModel()
        self.__fluid_model: AlkalineFluidModel = AlkalineFluidModel()
        self.__electrical_model: AlkalineElectricalModel = AlkalineElectricalModel(self.__pressure_model,
                                                                                   self.__fluid_model,
                                                                                   electrolyzer_data_config,
                                                                                   self.__parameters)
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
        power_cell: float = power / self.__number_cells     # W
        # calculation of current and voltage at stack level
        current_cell = self.__electrical_model.get_current(power_cell, state)  # A
        # TODO is this consideration of operating range valid?
        if (current_cell / (self.__electrical_model.get_geometric_area_cell() * 10000)) < self.__MIN_CURRENTDENSITY_CELL:
            current_cell = 0.0
        voltage_cell = self.__electrical_model.get_cell_voltage(current_cell, state)  # V
        stack_temperature = state.temperature           # °C
        stack_temperature = stack_temperature + 273.15  # K
        self.__current_stack = current_cell  # A  cells are serial connected to a Stack
        self.__current_cell = self.__current_stack
        self.__voltage_stack = voltage_cell * self.__number_cells  # V  cells are serial connected to one stack
        # calculation of pressures TODO more fitting variables for different pressures used in alkaline model
        molarity = self.__fluid_model.get_molarity(stack_temperature)
        self.__part_pressure_h2 = self.__pressure_model.get_partial_pressure_h2(molarity, stack_temperature)
        self.__part_pressure_o2 = self.__pressure_model.get_partial_pressure_o2(molarity, stack_temperature)
        # self.__sat_pressure_h2o = self.__pressure_model.get_sat_pressure_h2o(molarity, stack_temperature)
        # net use of water, production of hydrogen and oxygen at Stack level
        h2_net_cathode = self.__fluid_model.get_h2_generation_cell(self.__current_cell)  # mol/s
        o2_net_anode = self.__fluid_model.get_o2_generation_cell(self.__current_cell)  # mol/s
        h2o_net_use_cell: float = self.__fluid_model.get_h2o_use_cell(self.__current_cell)
        self.__h2o_use_stack = h2o_net_use_cell * self.__number_cells  # mol/s
        self.__o2_generation_stack = o2_net_anode * self.__number_cells  # mol/s
        self.__h2_generation_stack = h2_net_cathode * self.__number_cells  # mol/s

    def get_nominal_current_density(self):
        return self.__NOMINAL_CURRENT_DENSITY

    def get_reference_voltage_eol(self, resistance_increase, exchange_current_decrease) -> float:   # TODO replace placeholder
        return 0

    def get_current(self):
        return self.__current_stack

    def get_current_density(self):
        return self.__current_stack / (self.__electrical_model.get_geometric_area_cell() * 10000)

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
        return self.__number_cells * self.__electrical_model.get_geometric_area_cell()

    def get_nominal_stack_power(self):
        return self.__nominal_stack_power

    def get_heat_capacity_stack(self):
        return self.__heat_capacity_stack

    def get_thermal_resistance_stack(self):
        return self.__thermal_resistance_stack

    def get_water_in_stack(self):
        return self.__water_in_stack

    def get_partial_pressure_h2(self):
        return self.__part_pressure_h2

    def get_partial_pressure_o2(self):
        return self.__part_pressure_o2

    def get_sat_pressure_h2o(self):
        return self.__sat_pressure_h2o

    def get_efficiency_curve(self, hydrogen_state: ElectrolyzerState):
        return pd.DataFrame({'current density': pd.Series(np.arange(0, 1, 0.1)), 'cell efficiency': pd.Series(np.arange(0, 1, 0.1)),
                             'voltage efficiency': pd.Series(np.arange(0, 1, 0.1)),
                             'faraday efficiency': pd.Series(np.arange(0, 1, 0.1))})

    def close(self):
        self.__log.close()
