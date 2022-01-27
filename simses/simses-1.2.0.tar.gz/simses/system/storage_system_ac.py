from simses.commons.data.data_handler import DataHandler
from simses.commons.error import EndOfLifeError
from simses.commons.state.abstract_state import State
from simses.commons.state.parameters import SystemParameters
from simses.commons.state.system import SystemState
from simses.logic.power_distribution.power_distributor import PowerDistributor
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.dc_coupling.dc_coupler import DcCoupling
from simses.system.housing.abstract_housing import Housing
from simses.system.power_electronics.electronics import PowerElectronics
from simses.system.storage_system_dc import StorageSystemDC
from simses.system.thermal.model.system_thermal_model import SystemThermalModel


class StorageSystemAC:
    """
    AC storage system class manages all connections within the AC storage system. Connections are power electronics,
    further DC couplings (load/generation), housing, thermal model, auxiliaries, DC storage systems and its power
    distribution logic. DC couplings are handled as an interference and tried to be primarily fed by storage system
    power.
    """

    def __init__(self, state: SystemState, data_export: DataHandler, system_thermal_model: SystemThermalModel,
                 power_electronics: PowerElectronics, storage_systems: [StorageSystemDC], dc_couplings: [DcCoupling]
                 , housing: Housing, power_distributor: PowerDistributor):
        self.__data_export = data_export
        self.__system_state: SystemState = state
        self.__system_id: int = int(self.__system_state.get(SystemState.SYSTEM_AC_ID))
        self.__power_electronics: PowerElectronics = power_electronics
        self.__acdc_converter: str = self.__power_electronics.acdc_converter_type
        self.__system_thermal_model: SystemThermalModel = system_thermal_model
        self.__storage_systems: [StorageSystemDC] = storage_systems
        self.__dc_couplings: [DcCoupling] = dc_couplings
        self.__auxiliaries: [Auxiliary] = list()
        self.__auxiliaries.extend(self.__system_thermal_model.get_auxiliaries())
        self.__auxiliaries.extend(self.__power_electronics.get_auxiliaries())
        for storage_system in self.__storage_systems:
            self.__auxiliaries.extend(storage_system.get_auxiliaries())
            housing.add_component_volume(storage_system.volume)
        for dc_coupling in self.__dc_couplings:
            self.__auxiliaries.extend(dc_coupling.get_auxiliaries())
        self.__system_state = self.__get_current_state()
        self.__data_export.transfer_data(self.__system_state.to_export())  # initial timestep
        self.__power_distributor: PowerDistributor = power_distributor
        housing.add_component_volume(self.__power_electronics.volume)
        self.__system_thermal_model.update_air_parameters()
        self.__housing = housing

    def update(self, power: float, time: float) -> None:
        """
        Function to update the states of an AC storage system

        Parameters
        ----------
        power : ac target power (from energy management system)
        time : current simulation time

        Returns
        -------

        """
        state = self.__system_state
        state.ac_power = power
        # TODO Aux losses are calculated from last timestep. How to implement aux losses for current timestep?
        state.aux_losses = 0
        state.dc_power_additional = 0
        for aux in self.__auxiliaries:
            aux.update(time, state)
        for dc in self.__dc_couplings:
            dc.update(time, state)
        self.__power_electronics.update(time, state)

        states: [State] = list()
        for system in self.__storage_systems:
            states.append(system.state)

        # self.__system_thermal_model.calculate_temperature(time, state, states)

        self.__power_distributor.set(time, states, power)

        total_dc_power: float = state.dc_power_intermediate_circuit + state.dc_power_additional
        all_systems_ok: bool = True
        err_msg: str = ''
        for system in self.__storage_systems:
            # TODO how to decide whether to store additional dc load or generation? (MM)
            local_power: float = self.__power_distributor.get_power_for(total_dc_power, system.state)
            try:
                system.update(time, local_power)
            except EndOfLifeError as err:
                all_systems_ok = False
                err_msg = str(err)
        for system in self.__storage_systems:
            system.wait()
        state.time = time
        self.__system_state = self.__get_current_state()
        # Make sure to run the temperature model after running the DC System to represent ACDC losses for corner cases
        # of SOC=0 and SOC=1 correctly
        self.__system_thermal_model.calculate_temperature(time, self.__system_state, states)
        self.__data_export.transfer_data(self.__system_state.to_export())
        if not all_systems_ok:
            raise EndOfLifeError(err_msg)

    def __get_current_state(self) -> SystemState:
        """
        Calculation of current system state

        Returns
        -------
        SystemState:
            Current state of system
        """
        states = list()
        for system in self.__storage_systems:
            states.append(system.state)
        system_state: SystemState = SystemState.sum_parallel(states)
        system_state.set(SystemState.SYSTEM_AC_ID, self.__system_id)
        system_state.set(SystemState.SYSTEM_DC_ID, 0)
        system_state.time = self.__system_state.time
        system_state.temperature = self.__system_thermal_model.get_temperature()
        system_state.ambient_temperature = self.__system_thermal_model.get_ambient_temperature()
        system_state.solar_thermal_load = self.__system_thermal_model.get_solar_irradiation_thermal_load()
        system_state.hvac_thermal_power = self.__system_thermal_model.get_hvac_thermal_power()
        system_state.ac_power = self.__system_state.ac_power
        system_state.pe_losses = self.__system_state.pe_losses
        system_state.aux_losses = self.__system_state.aux_losses
        system_state.dc_power_additional = self.__system_state.dc_power_additional
        system_state.max_charge_power = min(system_state.max_charge_power, self.__power_electronics.max_power)
        system_state.max_discharge_power = min(system_state.max_discharge_power, self.__power_electronics.max_power)
        self.__power_electronics.update_ac_power_from(system_state)
        # Include power electronic fulfillment after reverse power calculation
        system_state.fulfillment *= self.__system_state.fulfillment
        return system_state

    def get_system_parameters(self) -> dict:
        parameters: dict = dict()
        parameters[SystemParameters.SYSTEM] = type(self).__name__
        parameters[SystemParameters.ID] = str(self.__system_id)
        parameters[SystemParameters.POWER_DISTRIBUTION] = type(self.__power_distributor).__name__
        parameters[SystemParameters.CONTAINER_NUMBER] = self.__housing.get_number_of_containers()
        parameters[SystemParameters.CONTAINER_TYPE] = type(self.__housing).__name__
        parameters[SystemParameters.ACDC_CONVERTER] = self.__acdc_converter
        auxiliaries: list = list()
        for aux in self.__auxiliaries:
            auxiliaries.append(type(aux).__name__)
        subsystems: list = list()
        for system in self.__storage_systems:
            subsystems.append(system.get_system_parameters())
        parameters[SystemParameters.AUXILIARIES] = auxiliaries
        parameters[SystemParameters.SUBSYSTEM] = subsystems
        return parameters

    @property
    def state(self) -> SystemState:
        """
        Returns current system state

        Returns
        -------
        SystemState:
            State of the ac system

        """
        return self.__system_state

    @property
    def max_power(self) -> float:
        return self.__power_electronics.max_power

    @property
    def system_id(self) -> int:
        return self.__system_id

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        self.__system_thermal_model.reset_profiles(ts_adapted)

    def close(self) -> None:
        """
        Closing all open resources in AC storage system

        Parameters
        ----------

        Returns
        -------

        """
        self.__power_electronics.close()
        self.__system_thermal_model.close()
        self.__power_distributor.close()
        for storage_system in self.__storage_systems:
            storage_system.close()
        for aux in self.__auxiliaries:
            aux.close()
        for dc_coupling in self.__dc_couplings:
            dc_coupling.close()
