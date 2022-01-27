from configparser import ConfigParser

from simses.commons.config.data.fuel_cell import FuelCellDataConfig
from simses.commons.config.simulation.fuel_cell import FuelCellConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.constants import Hydrogen
from simses.commons.log import Logger
from simses.commons.state.technology.fuel_cell import FuelCellState
from simses.technology.hydrogen.fuel_cell.pressure.no_pressure import NoPressureModel
from simses.technology.hydrogen.fuel_cell.pressure.pressure_model import PressureModel
from simses.technology.hydrogen.fuel_cell.stack.jupiter import JupiterFuelCell
from simses.technology.hydrogen.fuel_cell.stack.no_fuel_cell import NoFuelCell
from simses.technology.hydrogen.fuel_cell.stack.pem import PemFuelCell
from simses.technology.hydrogen.fuel_cell.stack.stack_model import \
    FuelCellStackModel
from simses.technology.hydrogen.fuel_cell.thermal.no_thermal_model import NoThermalModel
from simses.technology.hydrogen.fuel_cell.thermal.simple import SimpleThermalModel
from simses.technology.hydrogen.fuel_cell.thermal.thermal_model import ThermalModel


class FuelCellFactory:

    def __init__(self, config: ConfigParser):
        self.__log: Logger = Logger(type(self).__name__)
        self.__config_general: GeneralSimulationConfig = GeneralSimulationConfig(config)
        self.__config_fuel_cell: FuelCellConfig = FuelCellConfig(config)
        self.__config_fuel_cell_data: FuelCellDataConfig = FuelCellDataConfig()

    def create_state(self, system_id: int, storage_id: int, temperature: float,
                     fuel_cell: FuelCellStackModel) -> FuelCellState:
        state: FuelCellState = FuelCellState(system_id, storage_id)
        state.time = self.__config_general.start
        # state.power = 0  # W
        state.temperature = temperature - 273.15  # K -> °C
        state.power_loss = 0  # W
        state.fulfillment = 1.0  # p.u.
        state.soh = 1.0  # p.u.
        state.convection_heat = 0  # W
        state.hydrogen_use = 0  # mols
        state.hydrogen_inflow = 0  # mol/s
        state.oxygen_use = 0  # mol/s
        state.oxygen_inflow = 0  # mol/s
        state.pressure_cathode = Hydrogen.EPS  # barg
        state.pressure_anode = Hydrogen.EPS  # barg
        state.voltage = 1  # stays at 1 so that electrolyzer and fuel cell always see the power indepentently from the voltage a timestep before
        fuel_cell.calculate(0)
        state.voltage = fuel_cell.get_voltage()
        state.current = fuel_cell.get_current()
        state.current_density = fuel_cell.get_current_density()
        # state.power = fuel_cell.get_power()
        return state

    def create_fuel_cell_stack(self, fuel_cell: str, fuel_cell_maximal_power: float) -> FuelCellStackModel:
        if fuel_cell == PemFuelCell.__name__:
            self.__log.debug('Creating fuel cell as ' + fuel_cell)
            return PemFuelCell(fuel_cell_maximal_power, self.__config_fuel_cell_data)
        elif fuel_cell == JupiterFuelCell.__name__:
            self.__log.debug('Creating fuel cell as ' + fuel_cell)
            return JupiterFuelCell(fuel_cell_maximal_power, self.__config_fuel_cell_data)
        elif fuel_cell == NoFuelCell.__name__:
            self.__log.debug('Creating fuel cell as ' + fuel_cell)
            return NoFuelCell()
        else:
            options: [str] = list()
            options.append(PemFuelCell.__name__)
            options.append(JupiterFuelCell.__name__)
            options.append(NoFuelCell.__name__)
            raise Exception('Specified fuel cell ' + fuel_cell + ' is unknown. '
                                                                 'Following options are available: ' + str(options))

    def create_thermal_model(self, fuel_cell: FuelCellStackModel, temperature: float) -> ThermalModel:
        # TODO For which fuel cell do you want to include which thermal model?
        if type(fuel_cell).__name__ in [JupiterFuelCell.__name__]:
            return SimpleThermalModel(temperature)
        else:
            return NoThermalModel()

    def create_pressure_model(self, fuel_cell: FuelCellStackModel) -> PressureModel:
        # TODO For which fuel cell do you want to include which pressure model?
        return NoPressureModel()
        # if pressure_model_fc == NoPressureModelFc.__name__:
        #     self.__log.debug('Creatubg electrolyzer pressure model as ' + pressure_model_fc)
        #     return NoPressureModelFc()
        # else:
        #     options: [str] = list()
        #     options.append(NoPressureModelFc.__name__)
        #     raise Exception('Specified thermal model ' + pressure_model_fc + 'is unknown. '
        #                                                                      'Following options are available: ' + str(
        #         options))

    def close(self):
        self.__log.close()
