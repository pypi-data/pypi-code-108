from configparser import ConfigParser

from simses.commons.data.data_handler import DataHandler
from simses.commons.state.technology.fuel_cell import FuelCellState
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.system.auxiliary.pump.fixeta_centrifugal import FixEtaCentrifugalPump
from simses.system.auxiliary.water_heating.water_heater import WaterHeating
from simses.technology.hydrogen.fuel_cell.factory import FuelCellFactory
from simses.technology.hydrogen.fuel_cell.pressure.pressure_model import PressureModel
from simses.technology.hydrogen.fuel_cell.stack.no_fuel_cell import NoFuelCell
from simses.technology.hydrogen.fuel_cell.stack.stack_model import \
    FuelCellStackModel
from simses.technology.hydrogen.fuel_cell.thermal.thermal_model import ThermalModel


class FuelCell:

    """
    FuelCell is the top level class incorporating a FuelCellStackModel, a ThermalModel and a PressureModel. The
    specific classes are instantiated within the FuelCellFactory.
    """

    __PUMP_EFFICIENCY: float = 0.7

    def __init__(self, system_id: int, storage_id: int, fuel_cell: str, max_power: float,
                 temperature: float, config: ConfigParser, data_handler: DataHandler):
        super().__init__()
        self.__data_handler: DataHandler = data_handler
        self.__pump: Pump = FixEtaCentrifugalPump(self.__PUMP_EFFICIENCY)
        self.__water_heating: WaterHeating = WaterHeating()
        factory: FuelCellFactory = FuelCellFactory(config)
        self.__stack_model: FuelCellStackModel = factory.create_fuel_cell_stack(fuel_cell, max_power)
        self.__pressure_model: PressureModel = factory.create_pressure_model(self.__stack_model)
        self.__thermal_model: ThermalModel = factory.create_thermal_model(self.__stack_model, temperature)
        self.__state: FuelCellState = factory.create_state(system_id, storage_id, temperature, self.__stack_model)
        factory.close()
        self.__log_data: bool = not isinstance(self.__stack_model, NoFuelCell)
        self.__write_data()

    def update(self, time: float, power: float) -> None:
        """
        Updates current, voltage and hydrogen flow of hydrogen state

        Parameters
        ----------
        time :
        state :
        power :

        Returns
        -------

        """
        local_power = power if power < 0.0 else 0.0
        state: FuelCellState = self.__state
        self.__stack_model.update(local_power, state)
        self.__pressure_model.update(time, state)
        self.__thermal_model.update(time, state)
        state.time = time
        self.__write_data()

    def __write_data(self) -> None:
        if self.__log_data:
            self.__data_handler.transfer_data(self.__state.to_export())

    def get_auxiliaries(self) -> list:
        return list()

    @property
    def state(self) -> FuelCellState:
        return self.__state

    def close(self):
        self.__stack_model.close()
        self.__pressure_model.close()
        self.__thermal_model.close()
        self.__pump.close()
        self.__water_heating.close()
