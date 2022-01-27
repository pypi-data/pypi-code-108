from configparser import ConfigParser

from simses.commons.config.data.data_config import DataConfig


class PowerElectronicsConfig(DataConfig):
    """class top read Power Electronics data path"""

    def __init__(self, path: str = None, config: ConfigParser = None):
        super().__init__(path, config)
        self.__section: str = 'POWER_ELECTRONICS'

    @property
    def acdc_converter_data(self) -> str:
        """Returns directory of acdc converter data files"""
        return self.get_data_path(self.get_property(self.__section, 'ACDC_CONVERTER_DATA'))

    @property
    def sinamics_efficiency_file(self) -> str:
        """Returns filename for Siemens S120 converter"""
        return self.acdc_converter_data + self.get_property(self.__section, 'SINAMICS_EFFICIENCY_FILE')

    @property
    def aixcontrol_efficiency_file(self) -> str:
        """Returns filename for AixControl GmbH converter"""
        return self.acdc_converter_data + self.get_property(self.__section, 'AIXCONTROL_EFFICIENCY_FILE')

    @property
    def dcdc_converter_dir(self) -> str:
        """Returns directory of acdc converter data files"""
        return self.get_data_path(self.get_property(self.__section, 'DCDC_CONVERTER_DIR'))

    @property
    def pgs_efficiency_file(self) -> str:
        """Returns filename for Siemens S120 converter"""
        return self.dcdc_converter_dir + self.get_property(self.__section, 'PGS_EFFICIENCY_FILE')
