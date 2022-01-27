from configparser import ConfigParser

from simses.commons.config.data.data_config import DataConfig


class FuelCellDataConfig(DataConfig):

    def __init__(self, path: str = None, config: ConfigParser = None):
        super().__init__(path, config)
        self.__section: str = 'FUEL_CELL_DATA'

    @property
    def fuel_cell_data_dir(self) -> str:
        """Returns directory of fuelcell data files"""
        return self.get_data_path(self.get_property(self.__section, 'FUEL_CELL_DATA_DIR'))

    @property
    def pem_fuel_cell_pc_file(self) -> str:
        """Returns filename for polarisation curve for PEM-Fuelcell"""
        return self.fuel_cell_data_dir + self.get_property(self.__section, 'PEM_FUEL_CELL_PC_FILE')

    @property
    def pem_fuel_cell_power_file(self) -> str:
        """Returns filename for power curve for PEM-Fuelcell"""
        return self.fuel_cell_data_dir + self.get_property(self.__section, 'PEM_FUEL_CELL_POWER_FILE')

    @property
    def jupiter_fuel_cell_pc_file(self) -> str:
        """Returns filename for polarisation curve for Jupiter-Fuelcell"""
        return self.fuel_cell_data_dir + self.get_property(self.__section, 'JUPITER_FUEL_CELL_PC_FILE')

    @property
    def jupiter_fuel_cell_power_file(self) -> str:
        """Returns filename for power curve for Jupiter-Fuelcell"""
        return self.fuel_cell_data_dir + self.get_property(self.__section, 'JUPITER_FUEL_CELL_POWER_FILE')
