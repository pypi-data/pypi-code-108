from configparser import ConfigParser


class SystemParameters:
    """
    SystemParameters collects all static information of the storage system and writes it to the results folder.
    """

    SECTION: str = 'System'
    EXTENSION: str = '.txt'

    ID: str = 'id'
    SYSTEM: str = 'system'
    SUBSYSTEM: str = 'subsystems'
    PARAMETERS: str = 'parameters'

    # StorageSystemAC level
    AUXILIARIES: str = 'auxiliaries'
    POWER_DISTRIBUTION: str = 'power_distribution'
    CONTAINER_NUMBER: str = 'number_of_containers'
    CONTAINER_TYPE: str = 'container_type'
    ACDC_CONVERTER: str = 'acdc_converter'

    # StorageSystemDC level
    DCDC_CONVERTER: str = 'dcdc_converter'
    STORAGE_TECHNOLOGY: str = 'technology'
    BATTERIES: str = 'batteries'
    BATTERY_CIRCUIT: str = 'battery_circuit'
    CELL_TYPE: str = 'cell_type'
    NOMINAL_VOLTAGE: str = 'nominal_voltage'

    def __init__(self):
        self.__parameters: ConfigParser = ConfigParser()
        self.__parameters.add_section(self.SECTION)

    def set(self, parameter: str, value: str) -> None:
        """
        Setting a parameters value

        Parameters
        ----------
        parameter :
            Parameter provided by SystemParameter class
        value :
            value to be written to parameter as string

        Returns
        -------

        """
        self.__parameters.set(self.SECTION, parameter, value)

    def set_all(self, parameters: dict) -> None:
        """
        Setting all parameters to internal system parameters

        Parameters
        ----------
        parameters :
            a set of parameters written to system parameters

        Returns
        -------

        """
        for parameter, value in parameters.items():
            self.set(parameter, str(value))

    def write_parameters_to(self, path: str) -> None:
        """
        Writing system parameters to file in path

        Parameters
        ----------
        path :
            path of file to write parameters

        Returns
        -------

        """
        with open(path + self.get_file_name(), 'w') as file:
            self.__parameters.write(file)

    @classmethod
    def get_file_name(cls) -> str:
        """

        Returns
        -------
        str:
            file name of system parameters
        """
        return cls.__name__ + cls.EXTENSION
