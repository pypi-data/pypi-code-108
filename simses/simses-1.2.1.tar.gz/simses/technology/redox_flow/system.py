from configparser import ConfigParser

from simses.commons.data.data_handler import DataHandler
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.technology.redox_flow.degradation.capacity_degradation import CapacityDegradationModel
from simses.technology.redox_flow.electrochemical.control.redox_control_system import RedoxControlSystem
from simses.technology.redox_flow.factory import RedoxFlowFactory
from simses.technology.redox_flow.pump_algorithm.abstract_pump_algorithm import PumpAlgorithm
from simses.technology.redox_flow.stack.abstract_stack import StackModule
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.storage import StorageTechnology


class RedoxFlow(StorageTechnology):
    """The RedoxFlow class updates the electrochemical model that includes the redox control system, the
    degradation model and the pump algorithm."""

    __MAX_LOOPS = 10
    __ACCURACY = 1e-9

    def __init__(self, stack_type, power, voltage, capacity, pump_algorithm, temperature, data_export: DataHandler,
                 storage_id: int, system_id: int, config: ConfigParser):
        super().__init__()
        self.__factory: RedoxFlowFactory = RedoxFlowFactory(config)
        self.__max_power = power
        self.__capacity = capacity
        self.__electrolyte_system: ElectrolyteSystem = self.__factory.create_electrolyte_system(capacity, stack_type)
        self.__stack_module: StackModule = self.__factory.create_stack_module(stack_type, self.__electrolyte_system,
                                                                              voltage, power)
        self.__capacity_degradation_model: CapacityDegradationModel = self.__factory.create_degradation_model(capacity,
            self.__stack_module)
        pump_algorithm = self.__factory.check_pump_algorithm(pump_algorithm, stack_type)
        self.__pump: Pump = self.__factory.create_pumps(pump_algorithm)
        self.__pump_algorithm: PumpAlgorithm = self.__factory.create_pump_algorithm(self.__pump, self.__stack_module,
                                                                                    self.__electrolyte_system,
                                                                                    pump_algorithm)
        battery_management_system: RedoxControlSystem = self.__factory.create_redox_management_system(
            self.__stack_module, self.__electrolyte_system, self.__pump_algorithm)
        self.__redox_flow_state: RedoxFlowState = self.__factory.create_redox_flow_state_from(storage_id, system_id,
                                                                                              self.__stack_module,
                                                                                              capacity, temperature)
        self.__electrochemical_model = self.__factory.create_electrochemical_model(self.__stack_module,
                                                                                   battery_management_system,
                                                                                   self.__electrolyte_system,
                                                                                   self.__pump_algorithm)
        self.__time = self.__redox_flow_state.time
        self.__data_export: DataHandler = data_export
        self.__data_export.transfer_data(self.__redox_flow_state.to_export())

    def update(self):
        """
        Starts updating the calculation for the electrochemical model of the redox flow battery, which includes the
        battery management system requests.

        Returns
        -------
            None

        """
        rfbs = self.__redox_flow_state
        time = self.__time
        soc_start_time_step = self.__redox_flow_state.soc
        soc_stack_start_time_step = self.__redox_flow_state.soc_stack
        self.get_equilibrium_state_for(time, rfbs, soc_start_time_step, soc_stack_start_time_step)
        self.__pump_algorithm.update(rfbs, soc_start_time_step)
        self.__capacity_degradation_model.update(time, rfbs)
        rfbs.time = time
        self.__data_export.transfer_data(rfbs.to_export())

    def get_equilibrium_state_for(self, time: float, rfbs: RedoxFlowState, soc_start_time_step: float,
                                  soc_stack_start_time_step: float):
        for step in range(self.__MAX_LOOPS):
            old_resistance = rfbs.internal_resistance
            rfbs.soc_stack = soc_stack_start_time_step
            rfbs.soc = soc_start_time_step
            self.__electrochemical_model.update(time, rfbs)
            if (not self.__stack_module.dependent_parameters() or
                    (abs(rfbs.internal_resistance - old_resistance) < self.__ACCURACY)):
                break

    def set(self, time: float, current: float, voltage: float):
        """
        Sets the new simulation time an sets the power (current * voltage) of the RedoxFlowState for the next simulation
        time step.

        Parameters
        ----------
        time : float
            current time of the simulation
        current : float
            target current in A
        voltage : float
            target voltage in V

        Returns
        -------
            None
        """
        self.__time = time
        self.__redox_flow_state.power_in = current * voltage

    def distribute_and_run(self, time: float, current: float, voltage: float):
        self.set(time, current, voltage)
        self.update()

    @property
    def volume(self) -> float:
        """
        Volume of storage technology in m^3.

        Returns
        -------
        float:
            Redox flow volume in m^3.
        """
        """
        The volume of electrolyte and stacks are considered. 
        """
        thickness_end_plate = 0.06  # m
        # Geometric factor that describes by how much the flow frame (length x width) is larger than the electrode area
        flow_frame_dimension_factor = 1.5  # m

        energy_density_electrolyte = (self.__electrolyte_system.get_capacity_density() *
                                      self.__stack_module.get_nominal_voltage_cell())
        volume_electrolyte = self.__capacity * 3600 / energy_density_electrolyte

        volume_stacks = (((self.__stack_module.get_electrode_thickness() * self.__stack_module.get_cell_per_stack()) *
                         2 + 2 * thickness_end_plate) * self.__stack_module.get_specific_cell_area() / 10000 *
                         flow_frame_dimension_factor * self.__stack_module.get_parallel_scale() *
                         self.__stack_module.get_serial_scale())

        volume_system = volume_electrolyte + volume_stacks
        return volume_system

    @property
    def mass(self) -> float:
        """
        Mass of the storage technology in kg.

        Returns
        -------
        float:
            Mass in kg.
        """
        """
        The mass of electrolyte and stacks are considered. For the stack, an equation was established that takes into 
        account the mass of aluminum end plates, copper current collectors, and polypropylene flow frames, which are 
        scaled with the electrode area and the number of cells. 
        """
        c = 3.22E2
        d = 4.65E2

        energy_density_electrolyte_mass = (self.__electrolyte_system.get_capacity_density() *
                                           self.__stack_module.get_nominal_voltage_cell() /
                                           self.__electrolyte_system.get_electrolyte_density())
        mass_electrolyte = self.__capacity * 3600 / energy_density_electrolyte_mass  # kg

        mass_stacks = ((c + d * self.__stack_module.get_electrode_thickness() *
                       self.__stack_module.get_cell_per_stack()) * self.__stack_module.get_specific_cell_area() / 10000
                       * self.__stack_module.get_serial_scale() * self.__stack_module.get_parallel_scale())  # kg

        mass_system = mass_stacks + mass_electrolyte
        return mass_system

    @property
    def surface_area(self) -> float:
        """
        Surface area of the storage technology that can be impacted by confection m^2.

        Returns
        -------
        float:
            Surface area of the storage technology in m^2.
        """
        """
        The open surface area of the tanks and stacks are considered.
        Assumption: The tank volume is box-shaped and in the bottom of the housing. The bottom is facing the ground, 
        but the other walls are open to air flow. The stacks are mounted in racks and all sides are open to air flow.
        """
        thickness_end_plate = 0.06
        flow_frame_dimension_factor = 1.5

        energy_density_electrolyte = (self.__electrolyte_system.get_capacity_density() *
                                      self.__stack_module.get_nominal_voltage_cell())
        volume_electrolyte = self.__capacity * 3600 / energy_density_electrolyte
        width_tanks = volume_electrolyte ** (1 / 3)
        surface_tanks = 5 * width_tanks ** 2

        length_stack = ((self.__stack_module.get_electrode_thickness() * self.__stack_module.get_cell_per_stack()) *
                        2 + 2 * thickness_end_plate)
        width_stack = (self.__stack_module.get_specific_cell_area() / 10000 * flow_frame_dimension_factor * 2) ** (1/2)

        surface_stacks = (length_stack * width_stack * 3 + width_stack ** 2 * self.__stack_module.get_serial_scale() *
                          self.__stack_module.get_parallel_scale())

        surface_system = surface_tanks + surface_stacks
        return surface_system

    @property
    def specific_heat(self) -> float:
        """
        Specific heat of storage technology in J/(kgK).

        Returns
        -------
        float:
            Specific heat capacity in J/[kgK).
        """
        """
        The specific heat is a mean value for the electrolyte and stacks. 
        For the specific heat of the stack, an equation was established that takes into account the aluminum end plates, 
        copper current collectors, and polypropylene flow frames.
        """
        a = 2.84E5
        b = 7.91E5
        c = 3.22E2
        d = 4.65E2

        energy_density_electrolyte_mass = (self.__electrolyte_system.get_capacity_density() *
                                           self.__stack_module.get_nominal_voltage_cell() /
                                           self.__electrolyte_system.get_electrolyte_density())

        # Hoffmann, Lisa. Physical properties of a VRFB-electrolyte and their impact on the cell-performance.
        specific_heat_electrolyte = 2960  # J/(kgK)

        specific_heat_stack_mean = ((a + b * self.__stack_module.get_electrode_thickness() *
                                    self.__stack_module.get_cell_per_stack()) / (c * d *
                                    self.__stack_module.get_electrode_thickness() *
                                    self.__stack_module.get_cell_per_stack()))  # J/(kgK)

        mass_electrolyte = self.__capacity * 3600 / energy_density_electrolyte_mass  # kg
        mass_stacks = ((c + d * self.__stack_module.get_electrode_thickness() *
                       self.__stack_module.get_cell_per_stack()) * self.__stack_module.get_specific_cell_area() / 10000
                       * self.__stack_module.get_serial_scale() * self.__stack_module.get_parallel_scale())  # kg

        specific_heat_system = ((specific_heat_electrolyte * mass_electrolyte + specific_heat_stack_mean + mass_stacks)
                                / (mass_stacks + mass_electrolyte))

        return specific_heat_system

    @property
    def convection_coefficient(self) -> float:
        """
        Convective heat transfer coefficient of a redox flow battery.

        A value of 5 W/m^2/K is assumed for the convective heat transfer coefficient, which is in the same order of
        magnitude as the reported values from Tang et al. (2012) and Yan et al. (2016).
        If the thermal model is to be used for a particular redox flow battery geometry, the value must be adjusted with
        respect to the system specifications.
        Tang, Ao, et al. "Thermal modelling and simulation of the all-vanadium redox flow battery." Journal of Power
        Sources 203 (2012): 165-176.
        Yan, Yitao, et al. "Modelling and simulation of thermal behaviour of vanadium redox flow battery." Journal of
        Power Sources 322 (2016): 116-128.

        Returns
        -------
        float:
            Convective heat transfer coefficient in W/(m^2*K).
        """
        return 5

    def wait(self):
        pass

    def get_auxiliaries(self) -> [Auxiliary]:
        return [self.__pump]

    @property
    def state(self) -> RedoxFlowState:
        return self.__redox_flow_state

    def get_system_parameters(self) -> dict:
        return dict()

    def close(self):
        """Closing all resources in redox_flow_system"""
        self.__factory.close()
