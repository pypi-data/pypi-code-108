from configparser import ConfigParser

from simses.commons.config.data.data_config import DataConfig


class EnergyManagementDataConfig(DataConfig):
    """class top read Energy Management data path"""

    def __init__(self, path: str = None, config: ConfigParser = None):
        super().__init__(path, config)
        self.__section: str = 'ENERGY_MANAGEMENT_DATA'

    @property
    def energy_management_data(self) -> str:
        """Returns directory of energy management data files"""
        return self.get_data_path(self.get_property(self.__section, 'ENERGY_MANAGEMENT_DATA_DIR'))

    @property
    def linear_efficiency_notton_acdc_file(self) -> str:
        """Returns filename for coefficients of linearized efficiency of Notton ACDC converter"""
        return self.energy_management_data + self.get_property(self.__section, 'LINEARIZED_EFFICIENCY_Notton_ACDC_FILE')

    @property
    def linear_efficiency_sony_lfp_file(self) -> str:
        """Returns filename for coefficients of linearized efficiency of Sony LFP"""
        return self.energy_management_data + self.get_property(self.__section, 'LINEARIZED_EFFICIENCY_Sony_LFP_FILE')

    @property
    def linear_cyc_degradation_sony_lfp_file(self) -> str:
        """Returns filename for coefficients of linearized cyclic degradation of Sony LFP"""
        return self.energy_management_data + self.get_property(self.__section,
                                                               'LINEARIZED_CYC_DEGRADATION_Sony_LFP_FILE')

    @property
    def linear_cal_degradation_sony_lfp_file(self) -> str:
        """Returns filename for coefficients of linearized calendar degradation of Sony LFP"""
        return self.energy_management_data + self.get_property(self.__section,
                                                               'LINEARIZED_CAL_DEGRADATION_Sony_LFP_FILE')
