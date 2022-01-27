from configparser import ConfigParser

from simses.commons.config.data.data_config import DataConfig


class BatteryDataConfig(DataConfig):

    def __init__(self, path: str = None, config: ConfigParser = None):
        super().__init__(path, config)
        self.__section: str = 'BATTERY_DATA'

    @property
    def cell_data_dir(self) -> str:
        """Returns directory of cell data files"""
        return self.get_data_path(self.get_property(self.__section, 'CELL_DATA_DIR'))

    @property
    def lfp_sony_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of sony LFP"""
        return self.cell_data_dir + self.get_property(self.__section, 'LFP_SONY_OCV_FILE')

    @property
    def lfp_sony_degradation_capacity_file(self) -> str:
        """Returns filename for open circuit voltage of sony LFP"""
        return self.cell_data_dir + self.get_property(self.__section, 'LFP_SONY_DEGRADATION_CAPACITY_FILE')

    @property
    def lfp_sony_degradation_resistance_file(self) -> str:
        """Returns filename for open circuit voltage of sony LFP"""
        return self.cell_data_dir + self.get_property(self.__section, 'LFP_SONY_DEGRADATION_RESISTANCE_FILE')

    @property
    def lfp_sony_rint_file(self) -> str:
        """Returns filename for internal resistance of sony LFP"""
        return self.cell_data_dir + self.get_property(self.__section, 'LFP_SONY_RINT_FILE')

    @property
    def nca_panasonicNCR_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of panasonic NCA"""
        return self.cell_data_dir + self.get_property(self.__section, 'NCA_PANASONICNCR_OCV_FILE')

    @property
    def nca_panasonicNCR_rint_file(self) -> str:
        """Returns filename for internal resistance of panasonic NCA"""
        return self.cell_data_dir + self.get_property(self.__section, 'NCA_PANASONICNCR_RINT_FILE')

    @property
    def nmc_molicel_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of NMC Molicel"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Molicel_OCV_FILE')

    @property
    def nmc_molicel_rint_file(self) -> str:
        """Returns filename for internal resistance of NMC Molicel"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Molicel_RINT_FILE')

    @property
    def nmc_samsung94test_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of NMC 94Ah SamsungLabTest"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Samsung94AhTest_OCV_FILE')

    @property
    def nmc_samsung94test_rint_file(self) -> str:
        """Returns filename for internal resistance of NMC 94Ah SamsungLabTest"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Samsung94AhTest_RINT_FILE')

    @property
    def nmc_molicel_capacity_cal_file(self) -> str:
        """Returns filename for parameters for calendar aging of NMC Molicel"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Molicel_CAPACITY_CAL_FILE')

    @property
    def nmc_molicel_ri_cal_file(self) -> str:
        """Returns filename for parameters for calendar resistance increase of NMC Molicel"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Molicel_RI_CAL_FILE')

    @property
    def nmc_molicel_capacity_cyc_file(self) -> str:
        """Returns filename for parameters for cyclic aging of NMC Molicel"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Molicel_CAPACITY_CYC_FILE')

    @property
    def nmc_molicel_ri_cyc_file(self) -> str:
        """Returns filename for parameters for cyclic resistance increase of NMC Molicel"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Molicel_RI_CYC_FILE')

    @property
    def nmc_sanyo_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of sony Sanyo NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Sanyo_OCV_FILE')

    @property
    def nmc_sanyo_rint_file(self) -> str:
        """Returns filename for internal resistance of Sanyo NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Sanyo_RINT_FILE')

    @property
    def nmc_samsung_120ah_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of ads-tec Sanyo NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Samsung_120Ah_OCV_FILE')

    @property
    def nmc_samsung_120ah_rint_file(self) -> str:
        """Returns filename for internal resistance of ads-tec NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Samsung_120Ah_RINT_FILE')

    @property
    def nmc_samsung_120ah_capacity_cal_file(self) -> str:
        """Returns filename for calendar degradation of ads-tec NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Samsung_120Ah_CAPACITY_CAL_FILE')

    @property
    def nmc_akasol_akm_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of Akasol-AKM NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Akasol_AKM_OCV_FILE')

    @property
    def nmc_akasol_akm_rint_file(self) -> str:
        """Returns filename for internal resistance of Akasol-AKM NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Akasol_AKM_RINT_FILE')

    @property
    def nmc_akasol_oem_ocv_file(self) -> str:
        """Returns filename for open circuit voltage of Akasol-OEM NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Akasol_OEM_OCV_FILE')

    @property
    def nmc_akasol_oem_rint_file(self) -> str:
        """Returns filename for internal resistance of Akasol-OEM NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Akasol_OEM_RINT_FILE')

    @property
    def nmc_akasol_oem_current_file(self) -> str:
        """Returns filename for maximum current of Akasol-OEM NMC"""
        return self.cell_data_dir + self.get_property(self.__section, 'NMC_Akasol_OEM_CURRENT_FILE')

    @property
    def isea_cell_dir(self) -> str:
        """Returns dirname for isea cell files"""
        return self.get_data_path(self.get_property(self.__section, 'ISEA_CELL_DIR'))

    @property
    def lto_lmo_current_file(self) -> str:
        """Returns filename for lto_lmo cell files"""
        return self.cell_data_dir + self.get_property(self.__section, 'LTO_LMO_CURRENT_FILE')

    @property
    def lto_nmc_current_file(self) -> str:
        """Returns filename for lto_nmc cell files"""
        return self.cell_data_dir + self.get_property(self.__section, 'LTO_NMC_CURRENT_FILE')

    @property
    def sodium_ion_rint_green_rock_file(self) -> str:
        """Returns filename for internal resistance of sodium_ion Green Rock"""
        return self.cell_data_dir + self.get_property(self.__section, 'SODIUM_ION_RINT_GREEN_ROCK_FILE')

    @property
    def sodium_ion_ocv_green_rock_file(self) -> str:
        """Returns filename for open circuit voltage of sodium-ion Green Rock"""
        return self.cell_data_dir + self.get_property(self.__section, 'SODIUM_ION_OCV_GREEN_ROCK_FILE')