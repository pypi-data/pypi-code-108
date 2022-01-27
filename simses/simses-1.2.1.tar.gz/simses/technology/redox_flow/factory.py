from configparser import ConfigParser

from simses.commons.config.data.auxiliary import AuxiliaryDataConfig
from simses.commons.config.data.redox_flow import RedoxFlowDataConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.pump_algorithm.constant_pressure_pulsed import ConstantPressurePulsed
from simses.technology.redox_flow.pump_algorithm.fix_flow_rate_start_stop import FixFlowRateStartStop
from simses.technology.redox_flow.pump_algorithm.abstract_pump_algorithm import PumpAlgorithm
from simses.technology.redox_flow.pump_algorithm.stoich_flow_rate import StoichFlowRate
from simses.system.auxiliary.pump.fixeta_centrifugal import FixEtaCentrifugalPump
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.system.auxiliary.pump.scalable_variable_eta_centrifugal import ScalableVariableEtaCentrifugalPump
from simses.technology.redox_flow.degradation.const_hydrogen_current import ConstHydrogenCurrent
from simses.technology.redox_flow.degradation.no_degradation import NoDegradation
from simses.technology.redox_flow.degradation.variable_hydrogen_current import VariableHydrogenCurrent
from simses.technology.redox_flow.electrochemical.control.redox_control_system import RedoxControlSystem
from simses.technology.redox_flow.electrochemical.abstract_electrochemical import ElectrochemicalModel
from simses.technology.redox_flow.electrochemical.rint_model import RintModel
from simses.technology.redox_flow.stack.cell_data_stack_5500w import CellDataStack5500W
from simses.technology.redox_flow.stack.dummy_stack_3000w import DummyStack3000W
from simses.technology.redox_flow.stack.dummy_stack_5500W import DummyStack5500W
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.electrolyte.vanadium import VanadiumSystem
from simses.technology.redox_flow.stack.high_performance_stack_5700W import HighPerformanceStack5700W
from simses.technology.redox_flow.stack.industrial_stack_1500w import IndustrialStack1500W
from simses.technology.redox_flow.stack.industrial_stack_9000w import IndustrialStack9000W
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class RedoxFlowFactory:

    def __init__(self, config: ConfigParser):
        self.__log: Logger = Logger(type(self).__name__)
        self.__config_general: GeneralSimulationConfig = GeneralSimulationConfig(config)
        self.__config_redox_flow: RedoxFlowConfig = RedoxFlowConfig(config)
        self.__config_redox_flow_data: RedoxFlowDataConfig = RedoxFlowDataConfig()
        self.__config_auxiliary_data: AuxiliaryDataConfig = AuxiliaryDataConfig()

    def create_redox_flow_state_from(self, storage_id: int, system_id: int, stack_module: StackModule,
                                     capacity: float, temperature: float, redox_flow_state: RedoxFlowState = None):
        """
        Initial creates the RedoxFlowState object if it doesn't exist.

        Parameters
        ----------
        storage_id : int
            storage id
        system_id : int
            system id
        stack_module : StackModule
            stack module based on specific stack typ
        capacity : float
            Capacity of the electrolyte of the redox flow battery in Wh.
        temperature : float
            Temperature of the electrolyte of the redox flow battery in K.
        redox_flow_state : RedoxFlowState

        Returns
        -------
        RedoxFlowState
            state of the redox flow battery
        """
        if redox_flow_state is None:
            time: float = self.__config_general.start
            soc: float = self.__config_redox_flow.soc
            rfbs = RedoxFlowState(system_id, storage_id)
            rfbs.time = time
            rfbs.soc = soc
            rfbs.soc_stack = soc
            rfbs.soh = 1.0
            rfbs.voltage = stack_module.get_open_circuit_voltage(rfbs)
            rfbs.open_circuit_voltage = rfbs.voltage
            rfbs.current = 0.0
            rfbs.capacity = capacity
            rfbs.internal_resistance = stack_module.get_internal_resistance(rfbs)
            rfbs.power_loss = 0.0
            rfbs.power_in = 0.0
            rfbs.power = 0.0
            rfbs.pump_power = 0.0
            rfbs.pressure_loss_anolyte = 0.0
            rfbs.pressure_loss_catholyte = 0.0
            rfbs.pressure_drop_anolyte = 0.0
            rfbs.pressure_drop_catholyte = 0.0
            rfbs.flow_rate_anolyte = 0.0
            rfbs.flow_rate_catholyte = 0.0
            rfbs.fulfillment = 1.0
            rfbs.temperature = temperature
            rfbs.time_pump = 0.0
            rfbs.max_discharge_power = stack_module.get_max_power()
            rfbs.max_charge_power = stack_module.get_max_power()
            return rfbs
        else:
            return redox_flow_state

    def create_stack_module(self, stack_module: str, electrolyte_system: ElectrolyteSystem,
                            voltage: float, power: float) -> StackModule:
        """
        Initial creates the StackModule object for a specific stack typ.

        Parameters
        ----------
        stack_module : str
            stack type for stack module
        electrolyte_system : ElectrolyteSystem
            electrolyte system
        voltage : float
            nominal stack module voltage in V of the redox flow battery
        power : float
            nominal stack module power in W of the redox flow battery

        Returns
        -------
        StackModule
        """
        if stack_module == CellDataStack5500W.__name__:
            self.__log.debug('Creating stack module as ' + stack_module)
            return CellDataStack5500W(electrolyte_system, voltage, power, self.__config_redox_flow_data,
                                      self.__config_redox_flow)
        elif stack_module == DummyStack3000W.__name__:
            self.__log.debug('Creating stack module as ' + stack_module)
            return DummyStack3000W(electrolyte_system, voltage, power, self.__config_redox_flow)
        elif stack_module == DummyStack5500W.__name__:
            self.__log.debug('Creating stack module as ' + stack_module)
            return DummyStack5500W(electrolyte_system, voltage, power, self.__config_redox_flow)
        elif stack_module == IndustrialStack1500W.__name__:
            self.__log.debug('Creating stack module as ' + stack_module)
            return IndustrialStack1500W(electrolyte_system, voltage, power, self.__config_redox_flow_data,
                                        self.__config_redox_flow)
        elif stack_module == IndustrialStack9000W.__name__:
            self.__log.debug('Creating stack module as ' + stack_module)
            return IndustrialStack9000W(electrolyte_system, voltage, power, self.__config_redox_flow_data,
                                        self.__config_redox_flow)
        elif stack_module == HighPerformanceStack5700W.__name__:
            self.__log.debug('Creating stack module as ' + stack_module)
            return HighPerformanceStack5700W(electrolyte_system, voltage, power, self.__config_redox_flow_data,
                                             self.__config_redox_flow)
        else:
            options: [str] = list()
            options.append(CellDataStack5500W.__name__)
            options.append(DummyStack3000W.__name__)
            options.append(DummyStack5500W.__name__)
            options.append(IndustrialStack1500W.__name__)
            options.append(IndustrialStack9000W.__name__)
            options.append(HighPerformanceStack5700W.__name__)
            raise Exception('Specified stack module ' + stack_module + ' is unknown. '
                            'Following options are available: ' + str(options))

    def check_pump_algorithm(self, pump_algorithm: str, stack_module) -> str:
        if pump_algorithm == 'Default':
            if stack_module == CellDataStack5500W.__name__ or stack_module == DummyStack3000W.__name__ \
                    or stack_module == DummyStack5500W.__name__ or stack_module == HighPerformanceStack5700W.__name__:
                return StoichFlowRate.__name__
            elif stack_module == IndustrialStack1500W.__name__ or stack_module == IndustrialStack9000W.__name__:
                return ConstantPressurePulsed.__name__
        else:
            return pump_algorithm

    def create_pumps(self, pump_algorithm: str) -> Pump:
        if pump_algorithm == FixFlowRateStartStop.__name__:
            pump_type = FixEtaCentrifugalPump.__name__
            self.__log.debug('Creating pumps as ' + pump_type)
            # Value based on data from König (2017) (Dissertation)
            efficiency: float = 0.345
            return FixEtaCentrifugalPump(efficiency)
        # select if a special pump with a data file should be used
        # elif pump_algorithm == ConstantPressurePulsed.__name__:
        #     pump_type = 'VariableEtaCentrifugalPump'
        #     self.__log.debug('Creating pumps as ' + pump_type)
        #     return VariableEtaCentrifugalPump(self.__config_auxiliary_data)
        elif pump_algorithm == StoichFlowRate.__name__ or pump_algorithm == ConstantPressurePulsed.__name__:
            pump_type = ScalableVariableEtaCentrifugalPump.__name__
            self.__log.debug('Creating pumps as ' + pump_type)
            return ScalableVariableEtaCentrifugalPump()
        else:
            options: [str] = list()
            options.append(StoichFlowRate.__name__)
            options.append(FixFlowRateStartStop.__name__)
            options.append(ConstantPressurePulsed.__name__)
            raise Exception('Specified pump algorithm ' + pump_algorithm + ' is unknown. '
                            'Following options are available: ' + str(options))

    def create_electrolyte_system(self, capacity: float, stack_type: str):
        """
        Initial creates the ElectrolyteSystem object.

        Parameters
        ----------
        capacity : float
            Total start capacity of the redox flow system in Wh.
        stack_type: str
            stack type of the redox flow battery

        Returns
        -------
        ElectrolyteSystem
        """
        if (stack_type == CellDataStack5500W.__name__ or stack_type == DummyStack3000W.__name__ or
            stack_type == DummyStack5500W.__name__ or stack_type == IndustrialStack1500W.__name__ or
            stack_type == IndustrialStack9000W.__name__ or stack_type == HighPerformanceStack5700W.__name__):
            self.__log.debug('Creating electrolyte system as VanadiumSystem')
            return VanadiumSystem(capacity, self.__config_redox_flow)
        else:
            options: [str] = list()
            options.append(CellDataStack5500W.__name__)
            options.append(DummyStack3000W.__name__)
            options.append(DummyStack5500W.__name__)
            options.append(IndustrialStack1500W.__name__)
            options.append(IndustrialStack9000W.__name__)
            options.append(HighPerformanceStack5700W.__name__)
            raise Exception('Specified stack module for vanadium system ' + stack_type + ' is unknown. '
                            'Following options are available: ' + str(options))

    def create_electrochemical_model(self, stack_module: StackModule,
                                     battery_management_system: RedoxControlSystem
                                     , electrolyte_system: ElectrolyteSystem, pump_algorithm: PumpAlgorithm,
                                     electrochemical_model: ElectrochemicalModel = None) -> ElectrochemicalModel:
        """
        Initial creates the ElectrochemicalModel object for a specific model, which includes the battery management
        system requests.

        Parameters
        ----------
        stack_module : StackModule
            stack module of a redox flow battery
        battery_management_system : RedoxControlSystem
            battery management system of the redox flow battery
        electrolyte_system: ElectrolyteSystem
            electrolyte system of the redox flow battery
        pump_algorithm: PumpAlgorithm
            pump algorithm ot the redox flow battery
        electrochemical_model : ElectrochemicalModel
            electrochemical model of the redox flow battery

        Returns
        -------
            ElectrochemicalModel
        """
        if electrochemical_model is None:
            self.__log.debug('Creating electrochemical model for redox flow system depended on stack module ' +
                             stack_module.__class__.__name__)
            return RintModel(stack_module, battery_management_system, electrolyte_system, pump_algorithm)
        else:
            return electrochemical_model

    def create_redox_management_system(self, stack_module: StackModule, electrolyte_system: ElectrolyteSystem,
                                       pump_algorithm: PumpAlgorithm,
                                       redox_management_system: RedoxControlSystem = None) \
            -> RedoxControlSystem:
        """
        Initial creates the BatteryManagementSystem object of the redox flow battery.

        Parameters
        ----------
        stack_module : StackModule
            stack module of a redox flow battery
        electrolyte_system : ElectrolyteSystem
            management system of a redox flow battery
        pump_algorithm : PumpAlgorithm
            pump algorithm of the redox flow battery
        redox_management_system : RedoxControlSystem
            battery management system of the redox flow battery

        Returns
        -------
            RedoxControlSystem
        """
        if redox_management_system is None:
            self.__log.debug('Creating battery management system for redox flow system depended on stack module '
                             + stack_module.__class__.__name__)
            return RedoxControlSystem(stack_module, electrolyte_system, pump_algorithm, self.__config_redox_flow)
        else:
            return redox_management_system

    def create_degradation_model(self, capacity, stack_module: StackModule):
        # Degradation model can be changed here.
        degradation_model = 'ConstHydrogenCurrent'
        if degradation_model == 'NoDegradation':
            self.__log.debug('Creating degradation Model as ' + degradation_model)
            return NoDegradation(capacity)
        elif degradation_model == 'ConstHydrogenCurrent':
            self.__log.debug('Creating degradation Model as ' + degradation_model)
            return ConstHydrogenCurrent(capacity, stack_module)
        elif degradation_model == 'VariableHydrogenCurrent':
            self.__log.debug('Creating degradation Model as ' + degradation_model)
            return VariableHydrogenCurrent(capacity, stack_module, self.__config_redox_flow_data)
        else:
            options: [str] = list()
            options.append(NoDegradation.__name__)
            options.append(ConstHydrogenCurrent.__name__)
            options.append(VariableHydrogenCurrent.__name__)
            raise Exception('Specified degradation model ' + degradation_model + ' is unknown. '
                            'Following options are available: ' + str(options))

    def create_pump_algorithm(self, pump: Pump, stack_module: StackModule, electrolyte_system: ElectrolyteSystem,
                              pump_algorithm: str):
        if pump_algorithm == StoichFlowRate.__name__:
            self.__log.debug('Creating pump algorithm as ' + pump_algorithm)
            return StoichFlowRate(stack_module, pump, electrolyte_system, self.__config_redox_flow)
        elif pump_algorithm == FixFlowRateStartStop.__name__:
            self.__log.debug('Creating pump algorithm as ' + pump_algorithm)
            return FixFlowRateStartStop(stack_module, pump, electrolyte_system)
        elif pump_algorithm == ConstantPressurePulsed.__name__:
            self.__log.debug('Creating pump algorithm as ' + pump_algorithm)
            time_step = self.__config_general.timestep
            return ConstantPressurePulsed(stack_module, pump, electrolyte_system, int(time_step))
        else:
            options: [str] = list()
            options.append(StoichFlowRate.__name__)
            options.append(FixFlowRateStartStop.__name__)
            options.append(ConstantPressurePulsed.__name__)
            raise Exception('Specified pump algorithm ' + pump_algorithm + ' is unknown. '
                            'Following options are available: ' + str(options))

    def close(self):
        self.__log.close()
