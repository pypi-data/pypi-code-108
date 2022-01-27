from configparser import ConfigParser

from simses.commons.data.data_handler import DataHandler
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.energy_management_factory import EnergyManagementFactory
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class EnergyManagement:
    """
    Energy Management System to control the operation of the ESS.
    """

    def __init__(self, data_export: DataHandler, config: ConfigParser):
        self.__config: ConfigParser = config
        self.__factory: EnergyManagementFactory = EnergyManagementFactory(config)
        self.__operation_strategy: OperationStrategy = self.__factory.create_operation_strategy()
        self.__state: EnergyManagementState = self.__factory.create_energy_management_state()
        self.__data_export: DataHandler = data_export
        self.__data_export.transfer_data(self.__state.to_export())  # initial timestep

    def next(self, time: float, system_state: SystemState, power_offset: float = 0) -> float:
        """
        Return the next power value of the energy management strategy in W based on the operation strategy.

        Parameters
        ----------
        time : float
            Current timestamp.
        time_loop_delta:float
            Time delta due to current simulation loop.
        system_state : State
            Current state of the system.
        power : float
            Power value of stacked operation strategy.

        Returns
        -------
        float:
            Power value the StorageSystem should meet in W.

        """
        power = self.__operation_strategy.next(time, system_state, power_offset)
        self.__operation_strategy.update(self.__state)
        # Substract time loop delta for reading from profile csv
        # self.__state.time = time - time_loop_delta
        return power

    def export(self, time: float) -> None:
        self.__state.time = time
        self.__data_export.transfer_data(self.__state.to_export())

    def create_instance(self):
        return EnergyManagement(self.__data_export, self.__config)

    def close(self) -> None:
        """Closing open resources"""
        self.__operation_strategy.close()
        self.__factory.close()
