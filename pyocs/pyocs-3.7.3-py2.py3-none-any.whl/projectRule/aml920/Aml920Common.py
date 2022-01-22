import abc
from pyocs.pyocs_interface import UniteInterface
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *


class Aml920Common(UniteInterface):

    def get_board_macro(self):
        # CVT_DEF_BOARD_TYPE
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_TP_ATM30_" + board_type + "_SUB_" + sub_board_type + "_CH"
        ret = self.get_macro_line("CVT_DEF_BOARD_TYPE", board_macro)
        return ret

    def get_chip_macro(self):
        # CVT_DEF_CHIP_TYPE
        chip_remark = self.request_dict[self.ocs_demand.chip_remark]
        chip_type_str = self.request_dict[self.ocs_demand.chip_name]
        if 'T920L-B' in chip_type_str:
            ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_AMLT920L_DD_DDPLUS")
        else:
            ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_AMLT920L_NORMAL")
        return ret

    def get_flash_size_macro(self):
        # CVT_DEF_FLASH_SIZE
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_SIZE_" + flash_size
        ret = self.get_macro_line("CVT_DEF_FLASH_SIZE", flash_size_macro)
        return ret

    def get_pwm_macro(self):
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        if pwm_macro == '100':
            return ''
        else:
            return self.get_macro_line("CVT_DEF_CURRENT_REF_DUTY", pwm_macro)

    def get_wifi_macro(self):
        # WIFI TYPE
        ret = ''
        wifi_type_str = ''
        if not self.request_dict[self.ocs_demand.wifi_bluetooth_type]:
            if self.request_dict[self.ocs_demand.wifi_module_info]:
                wifi_type_str = self.request_dict[self.ocs_demand.wifi_module_info]
        else:
            wifi_type_str = self.request_dict[self.ocs_demand.wifi_bluetooth_type]

        return ret

    def get_ci_macro(self):
        ret = ''
        if (not self.request_dict[self.ocs_demand.ci_type]) and self.request_dict[self.ocs_demand.ciplus_name] == '无':
            pass
        elif 'CI_Plus' in self.request_dict[self.ocs_demand.ciplus_name]:
            ret += self.get_macro_line("CVT_DEF_CI_TYPE", "ID_CI_TYPE_CI_PLUS")
        elif "CI" in self.request_dict[self.ocs_demand.ci_type]:
            ret += self.get_macro_line("CVT_DEF_CI_TYPE", "ID_CI_TYPE_CI")
        return ret

    def get_eshare_macro(self):
        ret = ''
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        return ret

    def get_ddr_macro(self):
        ret = ''
        ddr_str = self.ocs_demand.get_ddr_size()
        if "512MB" in ddr_str:
            ret += self.get_macro_line("CVT_DEF_DDR_SIZE", "ID_DDR_512M")
        else:
            ret += self.get_macro_line("CVT_DEF_DDR_SIZE", "ID_DDR_1G")
        return ret

    def get_code_branch(self):
        return self._code_branch

    def get_tuner_macro(self):
        ret = ''
        tuner_type_str = self.request_dict[self.ocs_demand.tuner_name]
        if 'R842' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_TUNER_TYPE", "ID_TUNER_TYPE_RAFAEL_R842")
        elif 'MXL661' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_TUNER_TYPE", "ID_TUNER_TYPE_SILICON_MXL661")
        return ret

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass