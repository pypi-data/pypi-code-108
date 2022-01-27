from simses.commons.data.data_handler import DataHandler
from simses.commons.state.parameters import SystemParameters
from simses.commons.state.system import SystemState
from simses.commons.state.technology.storage import StorageTechnologyState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter
from simses.technology.storage import StorageTechnology


class StorageSystemDC:
    """
    DC storage system class incorporates a DCDC converter and a storage technology. In this class the power is split
    into current voltage via the DCDC converter based on the current storage technology state.
    """

    def __init__(self, system_id: int, storage_id: int, data_export: DataHandler, dcdc_converter: DcDcConverter,
                 storage_technology: StorageTechnology):
        self.__data_export: DataHandler = data_export
        self.__system_id: int = system_id
        self.__storage_id: int = storage_id
        # TODO Thermal model for dcdc converter needed? (MM, AP)
        self.__dcdc_converter: DcDcConverter = dcdc_converter
        self.__storage_technology: StorageTechnology = storage_technology
        self.__system_state: SystemState = self.__get_current_state()

    def update(self, time: float, dc_power: float) -> None:
        """
        Function to update the states of a DC storage system

        Parameters
        ----------
        time : current simulation time
        dc_power : DC target power (from ac storage system))

        Returns
        -------

        """
        # TODO implement current calculation in dcdc converter (MM)
        # self.__dcdc_converter.from_battery(dc_power, voltage_storage)
        # self.__dcdc_converter.to_battery(power, voltage_storage)

        voltage = self.__storage_technology.state.voltage
        self.__dcdc_converter.calculate_dc_current(dc_power, voltage)
        current: float = self.__dcdc_converter.dc_current
        self.__storage_technology.distribute_and_run(time, current, voltage)
        self.__system_state: SystemState = self.__get_current_state()

    def wait(self):
        """
        In case of multihreading in storage technologies, the upper storage system needs to wait for results.
        """
        self.__storage_technology.wait()

    def get_auxiliaries(self) -> [Auxiliary]:
        auxiliaries: [Auxiliary] = list()
        auxiliaries.extend(self.__dcdc_converter.get_auxiliaries())
        auxiliaries.extend(self.__storage_technology.get_auxiliaries())
        return auxiliaries

    @property
    def volume(self) -> float:
        """
        Volume of dc system in m3

        Returns
        -------

        """
        volume: float = 0.0
        volume += self.__storage_technology.volume
        volume += self.__dcdc_converter.volume
        return volume

    def __get_current_state(self) -> SystemState:
        system_state: SystemState = SystemState(self.__system_id, self.__storage_id)
        storage_state: StorageTechnologyState = self.__storage_technology.state
        system_state.time = storage_state.time
        system_state.fulfillment = storage_state.fulfillment
        system_state.soc = storage_state.soc
        system_state.capacity = storage_state.capacity
        system_state.soh = storage_state.soh
        system_state.temperature = storage_state.temperature
        system_state.max_charge_power = min(storage_state.max_charge_power, self.__dcdc_converter.max_power)
        system_state.max_discharge_power = min(storage_state.max_discharge_power, self.__dcdc_converter.max_power)
        system_state.storage_power_loss = storage_state.power_loss
        # reverse calculation
        system_state.dc_power_storage = storage_state.voltage * storage_state.current
        self.__dcdc_converter.reverse_calculate_dc_current(system_state.dc_power_storage, storage_state.voltage)
        system_state.dc_power_intermediate_circuit = self.__dcdc_converter.dc_power
        system_state.dc_power_loss = self.__dcdc_converter.dc_power_loss
        system_state.dc_circuit_voltage = self.__dcdc_converter.intermediate_circuit_voltage
        system_state.dc_current = self.__dcdc_converter.dc_current
        return system_state

    @property
    def state(self) -> SystemState:
        """
        Function to write dc states into SystemState

        Parameters
        -------

        Returns
        -------
        SystemState
           SystemState with all values from a dc system
        """
        return self.__system_state

    def get_system_parameters(self):
        parameters: dict = dict()
        parameters[SystemParameters.SYSTEM] = type(self).__name__
        parameters[SystemParameters.ID] = str(self.__system_id) + '.' + str(self.__storage_id)
        parameters[SystemParameters.STORAGE_TECHNOLOGY] = type(self.__storage_technology).__name__
        parameters[SystemParameters.DCDC_CONVERTER] = type(self.__dcdc_converter).__name__
        parameters.update(self.__storage_technology.get_system_parameters())
        return parameters

    def get_storage_technology(self) -> StorageTechnology:
        return self.__storage_technology

    def get_dc_dc_converter(self) -> DcDcConverter:
        return self.__dcdc_converter

    def close(self) -> None:
        """
        Closing all open resources in a DC storage system

        Parameters
        ----------

        Returns
        -------

        """
        self.__storage_technology.close()
        self.__dcdc_converter.close()
