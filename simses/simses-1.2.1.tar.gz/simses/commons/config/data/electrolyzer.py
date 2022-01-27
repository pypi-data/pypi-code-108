from configparser import ConfigParser

from simses.commons.config.data.data_config import DataConfig


class ElectrolyzerDataConfig(DataConfig):

    def __init__(self, path: str = None, config: ConfigParser = None):
        super().__init__(path, config)
        self.__section: str = 'ELECTROLYZER_DATA'

    @property
    def lookuptable_dir(self) -> str:
        """Returns directory of electrolyzer data files"""
        return self.get_data_path(self.get_property(self.__section, 'ELECTROLYZER_LOOKUPTABLE_DATA_DIR'))

    @property
    def parameters_dir(self) -> str:
        """Returns directory of electrolyzer data files"""
        return self.get_data_path(self.get_property(self.__section, 'ELECTROLYZER_PARAMETERS_DATA_DIR'))

    @property
    def pem_electrolyzer_pc_file(self) -> str:
        """Returns filename for polarisation curve for PEM-Electrolyzer"""
        return self.lookuptable_dir + self.get_property(self.__section, 'PEM_ELECTROLYZER_PC_FILE')

    @property
    def pem_electrolyzer_power_file(self) -> str:
        """Returns filename for power curve for PEM-Electrolyzer"""
        return self.lookuptable_dir + self.get_property(self.__section, 'PEM_ELECTROLYZER_POWER_FILE')

    @property
    def pem_electrolyzer_multi_dim_analytic_para_file(self) -> str:
        """Returns filename for power curve for PEM-Electrolyzer"""
        return self.parameters_dir + self.get_property(self.__section, 'PEM_ELECTROLYZER_MULTI_DIM_ANALYTIC_PARA_FILE')

    @property
    def alkaline_electrolyzer_multidim_lookup_currentdensity_file(self) -> str:
        """Returns filename for power curve for Alkaline Electrolyzer"""
        return self.lookuptable_dir + self.get_property(self.__section,'ALKALINE_ELECTROLYZER_CURRENT_FILE')

    @property
    def alkaline_electrolyzer_fit_para_file(self) -> str:
        """Returns filename for power curve for PEM-Electrolyzer"""
        return self.parameters_dir + self.get_property(self.__section, 'ALKALINE_ELECTROLYZER_FIT_PARA_FILE')
