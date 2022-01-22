import abc
from pyocs.pyocs_interface import UniteInterface


class Mtk5522Common(UniteInterface):

    isdb_chip = ('MT5522EHMJ', 'MT5522VHOJ', 'MT5522VHMJ', 'MT5522DHOJ', 'MT5522DHMJ', 'MT5522EHMJ')
    dvb_chip = ('MT5522ZHOJ', 'MT5522ZHMJ', 'MT5522HHMJ', 'MT5522HHOJ', 'MT5522ZHMJ')

    def get_board_macro(self):
        # 主板宏：CVT_DEF_BOARD_TYPE  ID_BD_[主方案:MTK5522]_[板型:81]_SUB_CH_[子板型:A1]
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[1].rstrip('S')
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_CH_" + sub_board_type
        ret = "#define CVT_DEF_BOARD_TYPE".ljust(self._space) + board_macro + '\n'
        return ret

    def get_chip_macro(self):
        # 主芯片宏：CVT_DEF_CHIP_TYPE ID_CHIP_[芯片名：MT5522ZHOJ]
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        chip_macro = "ID_CHIP_" + chip_type
        ret = "#define CVT_DEF_CHIP_TYPE".ljust(self._space) + chip_macro + '\n'
        return ret

    def get_flash_size_macro(self):
        # Flash Size宏：ID_FLASH_SIZE_[Flash Size：8G]
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_SIZE_" + flash_size
        ret = "#define CVT_DEF_FLASH_SIZE".ljust(self._space) + flash_size_macro + '\n'
        return ret

    def get_pwm_macro(self):
        # Pwm占空比宏：[占空比：60]
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        ret = "#define CVT_DEF_PWM_REF_MAX".ljust(self._space) + pwm_macro + '\n'
        return ret

    def get_wifi_macro(self):
        # WIFI TYPE
        ret = ''
        wifi_type_str = ''
        if not self.request_dict[self.ocs_demand.wifi_bluetooth_type]:
            if self.request_dict[self.ocs_demand.wifi_module_info]:
                wifi_type_str = self.request_dict[self.ocs_demand.wifi_module_info]
        else:
            wifi_type_str = self.request_dict[self.ocs_demand.wifi_bluetooth_type]
        if 'M06USA1' in wifi_type_str:
            ret = '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_MT7601U' + '\n'
        elif 'M603USA1' in wifi_type_str:
            ret = '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_MT7603U' + '\n'
        elif 'M632USA1' in wifi_type_str:
            ret = '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_MT7662U' + '\n'
        elif 'RTK8192' in wifi_type_str:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_RTK8192' + '\n'
        elif 'SKI.W6022.1' in wifi_type_str:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_ATBM6022' + '\n'
        return ret

    def get_ci_macro(self):
        # CI PLUS
        ret = ''
        if (not self.request_dict[self.ocs_demand.ci_type]) and (not self.request_dict[self.ocs_demand.ciplus_name]):
            ret = '#define CVT_DEF_CI_TYPE'.ljust(self._space) + 'ID_CI_TYPE_NONE' + '\n'
        elif 'CI_Plus' in self.request_dict[self.ocs_demand.ciplus_name]:
            ret = '#define CVT_DEF_CI_TYPE'.ljust(self._space) + 'ID_CI_TYPE_CI_PLUS' + '\n'
        elif "CI" in self.request_dict[self.ocs_demand.ci_type]:
            ret = '#define CVT_DEF_CI_TYPE'.ljust(self._space) + 'ID_CI_TYPE_CI' + '\n'
        return ret

    def get_eshare_macro(self):
        # ESHARE
        other_app_list = self.ocs_demand.get_other_app_software()
        if other_app_list and 'Eshare' in other_app_list:
            ret = '#define CVT_EN_APP_ESHARE'.ljust(self._space) + '1' + '\n'
        else:
            ret = '#define CVT_EN_APP_ESHARE'.ljust(self._space) + '0' + '\n'
        return ret

    def get_ddr_macro(self):
        ret = ''
        ddr_str = self.ocs_demand.get_ddr_size()
        if "1.25G" in ddr_str:
            ret = '#define CVT_DEF_DDR_SIZE'.ljust(self._space) + 'ID_DDR_1P25G' + '\n'
        elif "1G" in ddr_str:
            ret = '#define CVT_DEF_DDR_SIZE'.ljust(self._space) + 'ID_DDR_1G' + '\n'
        return ret

    def get_tuner_type_macro(self):
        ret = ""
        tuner_str = self.ocs_demand.get_tuner_type()
        if "EDS-11980FNPRD" in tuner_str:
            ret = '#define CVT_DEF_SECOND_TUNER_TYPE'.ljust(self._space) + \
                  'ID_TUNER_TYPE_RAFAEL_RT710_EDS_11980FNPRD' + '\n'
        return ret

    def get_code_branch(self):
        return self._code_branch

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass
