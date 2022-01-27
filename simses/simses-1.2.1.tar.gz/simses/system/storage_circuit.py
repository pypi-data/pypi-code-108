from configparser import ConfigParser
from simses.commons.data.data_handler import DataHandler
from simses.commons.error import EndOfLifeError
from simses.commons.state.abstract_state import State
from simses.commons.state.parameters import SystemParameters
from simses.commons.state.system import SystemState
from simses.logic.power_distribution.power_distributor import PowerDistributor
from simses.system.factory import StorageSystemFactory
from simses.system.storage_system_ac import StorageSystemAC


class StorageCircuit:

    """
    StorageCircuit is the top level class including all AC storage systems. The is distributed via a PowerDistributor
    logic to each AC storage system.
    """

    def __init__(self, data_export: DataHandler, config: ConfigParser):
        factory: StorageSystemFactory = StorageSystemFactory(config)
        self.__storage_systems: [StorageSystemAC] = factory.create_storage_systems_ac(data_export)
        self.__power_distributor: PowerDistributor = factory.create_power_distributor_ac()
        factory.close()

    def update(self, time: float, power: float, power_dist: [float] = None) -> None:
        if power_dist is None:
            power_dist = []
        states: [State] = list()
        for system in self.__storage_systems:
            states.append(system.state)
        self.__power_distributor.set(time, states, power)
        end_of_life_reached: bool = False
        for i in range(0, len(self.__storage_systems)):
            if not power_dist:
                local_power: float = self.__power_distributor.get_power_for(power, self.__storage_systems[i].state)
            else:
                local_power: float = power_dist[i]
            try:
                self.__storage_systems[i].update(local_power, time)
            except EndOfLifeError:
                end_of_life_reached = True
        if end_of_life_reached:
            raise EndOfLifeError()

    @property
    def state(self) -> SystemState:
        system_states = list()
        for storage in self.__storage_systems:
            system_states.append(storage.state)
        system_state: SystemState = SystemState.sum_parallel(system_states)
        system_state.set(SystemState.SYSTEM_AC_ID, 0)
        system_state.set(SystemState.SYSTEM_DC_ID, 0)
        return system_state

    @property
    def ac_system_states(self) -> [SystemState]:
        system_states = list()
        for storage in self.__storage_systems:
            system_states.append(storage.state)
        return system_states

    def get_system_parameters(self) -> dict:
        parameters: dict = dict()
        subsystems: list = list()
        for system in self.__storage_systems:
            subsystems.append(system.get_system_parameters())
        parameters[SystemParameters.POWER_DISTRIBUTION] = type(self.__power_distributor).__name__
        parameters[SystemParameters.SUBSYSTEM] = subsystems
        return {SystemParameters.PARAMETERS: parameters}

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        for system in self.__storage_systems:
            system.reset_profiles(ts_adapted)

    def close(self) -> None:
        """Closing all resources in storage systems"""
        self.__power_distributor.close()
        for storage in self.__storage_systems:
            storage.close()
