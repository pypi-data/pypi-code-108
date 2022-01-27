from configparser import ConfigParser

from simses.commons.data.data_handler import DataHandler
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.system.auxiliary.gas_drying.gas_dryer import GasDrying
from simses.system.auxiliary.gas_drying.hydrogen import HydrogenGasDrying
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.system.auxiliary.pump.fixeta_centrifugal import FixEtaCentrifugalPump
from simses.system.auxiliary.water_heating.water_heater import WaterHeating
from simses.technology.hydrogen.electrolyzer.degradation.degradation_model import DegradationModel
from simses.technology.hydrogen.electrolyzer.factory import ElectrolyzerFactory
from simses.technology.hydrogen.electrolyzer.pressure.abstract_model import PressureModel
from simses.technology.hydrogen.electrolyzer.stack.no_electrolyzer import NoElectrolyzer
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel
from simses.technology.hydrogen.electrolyzer.thermal.abstract_model import ThermalModel


class Electrolyzer:
    """
    Electrolyzer is the top level class incorporating a ElectrolyzerStackModel, a ThermalModel and a PressureModel. The
    specific classes are instantiated within the ElectrolyzerFactory.
    """

    __PUMP_EFFICIENCY: float = 0.7

    def __init__(self, system_id: int, storage_id: int, electrolyzer: str, max_power: float,
                 temperature: float, config: ConfigParser, data_handler: DataHandler):
        super().__init__()
        self.__data_handler: DataHandler = data_handler
        self.__pump: Pump = FixEtaCentrifugalPump(self.__PUMP_EFFICIENCY)
        self.__gas_drying: GasDrying = HydrogenGasDrying()
        self.__water_heating: WaterHeating = WaterHeating()
        factory: ElectrolyzerFactory = ElectrolyzerFactory(config)
        self.__stack_model: ElectrolyzerStackModel = factory.create_electrolyzer_stack(electrolyzer, max_power)
        self.__pressure_model: PressureModel = factory.create_pressure_model(self.__stack_model)
        self.__thermal_model: ThermalModel = factory.create_thermal_model(self.__stack_model, self.__water_heating,
                                                                          self.__pump, temperature)
        self.__degradation_model: DegradationModel = factory.create_degradation_model(self.__stack_model)
        self.__state: ElectrolyzerState = factory.create_state(system_id, storage_id, temperature,
                                                               self.__stack_model, self.__pressure_model)
        factory.close()
        self.__log_data: bool = not isinstance(self.__stack_model, NoElectrolyzer)
        self.__write_data()

    def update(self, time: float, power: float) -> None:
        """
        Updates hydrogen states that are corrolated with the electrolyzer such as current, voltage, hydrogen production,
        water use and temperature

        Parameters
        ----------
        time :
        hydrogen_state :
        power :

        Returns
        -------

        """
        local_power = power if power > 0.0 else 0.0
        state = self.__state
        self.__stack_model.update(local_power, state)
        state.power = local_power  # TODO: is at this point clear if the electrolyzer can take all of the supplied power?

        # state values that will be needed before they were updated
        pressure_cathode_0 = state.pressure_cathode  # barg
        pressure_anode_0 = state.pressure_anode  # barg

        # update temperature and pressure of the stack
        self.__pressure_model.update(time, state)
        state.water_use += state.water_outflow_cathode + state.water_outflow_anode
        self.__thermal_model.update(time, state, pressure_cathode_0, pressure_anode_0)
        # self.convection_heat_el = self.__thermal_model.get_convection_heat()

        # update degradation of stack
        state.reference_voltage = self.__stack_model.get_reference_voltage_eol(state.resistance_increase,
                                                                                  state.exchange_current_decrease)
        self.__degradation_model.update(time, state)

        # update auxilliary losses
        state.power_water_heating = self.__thermal_model.get_power_water_heating()
        # pressure_loss: float = self.__thermal_model.get_tube_pressure_loss() * state.water_flow * \
        #                        ConstantsHydrogen.MOLAR_MASS_WATER / ConstantsHydrogen.DENSITY_WATER
        # self.__pump.calculate_pump_power(pressure_loss)
        state.power_pump = self.__pump.get_pump_power()
        self.__gas_drying.calculate_gas_drying_power(pressure_cathode_0+1, state.hydrogen_outflow)
        state.power_gas_drying = self.__gas_drying.get_gas_drying_power()
        state.time = time
        self.__write_data()

    def __write_data(self) -> None:
        if self.__log_data:
            self.__data_handler.transfer_data(self.__state.to_export())

    def get_auxiliaries(self):
        return [self.__gas_drying, self.__water_heating, self.__pump]

    @property
    def state(self) -> ElectrolyzerState:
        return self.__state

    def close(self):
        self.__stack_model.close()
        self.__pressure_model.close()
        self.__thermal_model.close()
        self.__degradation_model.close()
        self.__pump.close()
        self.__water_heating.close()
