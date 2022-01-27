import math
from abc import ABC, abstractmethod

from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem


class StackModule(ABC):
    """A StackModule describes a module of electrical serial and parallel connected redox flow stacks."""

    def __init__(self, electrolyte_system: ElectrolyteSystem, voltage: float, power: float, cell_number_per_stack: int,
                 stack_power: float, redox_flow_config: RedoxFlowConfig):
        super().__init__()
        self.__log: Logger = Logger(self.__class__.__name__)
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__exact_size = redox_flow_config.exact_size
        serial, parallel = self.__stack_connection(voltage, power, cell_number_per_stack, stack_power)
        self._SERIAL_SCALE: float = serial
        self._PARALLEL_SCALE: float = parallel
        self.__max_power = serial * parallel * stack_power * 2
        self.__log.debug('Stacks serial: ' + str(serial) + ', parallel: ' + str(parallel))

    def __stack_connection(self, voltage: float, power: float, cell_number_per_stack: int, stack_power: float):
        """
        Calculates the number of serial and parallel connected stacks in a stack module to obtain the system voltage and
        power.

        Parameters
        ----------
        voltage : float
            Voltage of the system in V.
        power : float
            Power of the system in W.
        cell_number_per_stack : int
            Number of cells per stack.
        stack_power : float
            Nominal power of one stack.

        Returns
        -------
            Serial number of stacks connected in a stack module.
            Parallel number of stacks connected in a stack module.
        """
        stack_voltage = (cell_number_per_stack * self.get_nominal_voltage_cell())
        if self.__exact_size:
            number_stacks: float = power / stack_power
            serial: float = min(voltage / stack_voltage, number_stacks)
            parallel: float = number_stacks / serial
            return serial, parallel
        else:
            # integer serial and parallel stack numbers, highest number used
            number_stacks: int = math.ceil(power / stack_power)
            serial: int = min(math.ceil(voltage / stack_voltage), number_stacks)
            parallel: int = math.ceil(number_stacks / serial)
            return serial, parallel

    @abstractmethod
    def get_open_circuit_voltage(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Calculates the open circuit voltage (OCV) of a stack module depended on the electrolyte.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float:
            OCV of the stack module in V.
        """
        pass

    @abstractmethod
    def get_nominal_voltage_cell(self) -> float:
        """
        Returns the nominal voltage of a single cell of a stack module in V. The value is used to change the capacity
        in Ws to its value in As and vice versa. The value of the OCV at SOC = 50 % and temperature = 30 °C is used.

        Returns
        -------
        float:
           Nominal cell voltage in V.
        """
        pass

    @abstractmethod
    def get_internal_resistance(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Determines the internal resistance of the stack module based on the current RedoxFlowState.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float:
            Internal resistance of the stack module in Ohm.
        """
        pass

    @abstractmethod
    def get_cell_per_stack(self) -> int:
        """
        Determines the cells per stack for the used stack type.

        Returns
        -------
        int:
            Number of cells per stack.
        """
        pass

    @abstractmethod
    def get_min_voltage(self) -> float:
        """
        Determines the minimal voltage of a stack module.

        Returns
        -------
        float:
            Minimal stack module voltage in V.
        """
        pass

    @abstractmethod
    def get_max_voltage(self) -> float:
        """
        Determines the maximal voltage of a stack module.

        Returns
        -------
        float:
            Maximal stack module voltage in V.
        """
        pass

    @abstractmethod
    def get_self_discharge_current(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Determines the self-discharge current that discharges the stack module during standby and which accounts for
        self-discharge losses during cycling (Coulomb efficiency). The connection of multiple cells and stacks is
        considered.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float:
            Total self-discharge current for a stack module in A.
        """
        pass

    @abstractmethod
    def get_specific_cell_area(self) -> float:
        """
        Returns the specific geometrical electrode area in cm^2. This corresponds to the area of the electrode that
        presses on the membrane.

        Returns
        -------
        float:
            Cell area in cm^2.
        """
        pass

    def get_electrode_thickness(self) -> float:
        """
        Returns the electrode thickness in m.

        Returns
        -------
        float:
            Electrode thickness in m.
        """
        pass

    @abstractmethod
    def get_electrode_porosity(self) -> float:
        """
        Returns the electrode porosity.

        Returns
        -------
        float:
            Electrode porosity.
        """
        pass

    @abstractmethod
    def get_hydraulic_resistance(self) -> float:
        """
        Returns the hydraulic resistance of the system in 1/m^3. The electrolyte flows through all stacks parallel.

        Returns
        -------
        float:
            Hydraulic resistance in 1/m^3.
        """
        pass

    def get_stacks_electrolyte_volume(self) -> float:
        """
        Returns the volume of electrolyte in the stack module electrodes in m^3 for one electrolyte side.

        Returns
        -------
        float:
            Electrolyte volume in the electrodes of the stack module in m^3.
        """
        stack_electrolyte_volume = (self.get_specific_cell_area() * self.get_electrode_thickness() / 10000 *
                                    self.get_cell_per_stack() * self.get_serial_scale() * self.get_parallel_scale() *
                                    self.get_electrode_porosity())
        if self.get_total_electrolyte_volume() < stack_electrolyte_volume:
            return self.get_total_electrolyte_volume()
        else:
            return stack_electrolyte_volume

    def get_total_electrolyte_volume(self) -> float:
        """
        Returns the total volume of the electrolyte of on electrolyte side (anolyte or catholyte).

        Returns
        -------
        float:
            Electrolyte volume of one side in m^3.
        """
        electrolyte_volume = (self.__electrolyte_system.get_start_capacity() * 3600 / (self.__electrolyte_system.FARADAY
                              * self.__electrolyte_system.get_vanadium_concentration() *
                              self.get_nominal_voltage_cell()))
        return electrolyte_volume

    def get_max_current_low_soc(self) -> float:
        """
        Determines the maximal current of the stack module at the lowest soc.

        Returns
        -------
        float:
            Maximal current in A.
        """
        return self.__max_power / self.get_min_voltage()

    def get_max_current_high_soc(self) -> float:
        """
        Determines the maximal current at the maximal voltage.

        Returns
        -------
        float:
            Maximal current in A at the maximal voltage.
        """
        return self.__max_power / 2 / self.get_max_voltage()

    def get_max_power(self) -> float:
        """
        Returns the maximal power of the redox flow system.

        Returns
        -------
        float:
            Maximal Power of the redox flow system in W.
        """
        return self.__max_power

    def dependent_parameters(self) -> bool:
        """
        Boolean value that signals whether parameters for the electrochemical model are dependent on voltage or current
        and therefore require iterations (e. q. the internal resistance is dependent on the current).

        Returns
        -------
        bool:
            True if parameters for the electrochemical model are dependent on voltage or current.
        """
        pass

    def get_name(self) -> str:
        """
        Determines the class name of a stack typ  (e. g. CellDataStack5500W).

        Returns
        -------
        str:
            Class name of a stack typ.
        """
        return self.__class__.__name__

    def get_serial_scale(self) -> float:
        """
        Returns the serial scale of stacks in the stack module. The value can be float if exact_size is true.

        Returns
        -------
        float:
            Number of serial stacks in the stack module.
        """
        return self._SERIAL_SCALE

    def get_parallel_scale(self) -> float:
        """
        Returns the parallel scale of stacks in the stack module. The value can be float if exact_size is true.

        Returns
        -------
        float:
            Number of parallel stacks in the stack module.
        """
        return self._PARALLEL_SCALE

    @abstractmethod
    def close(self):
        """Closing all resources in StackModule."""
        self.__log.close()
        self.__electrolyte_system.close()
