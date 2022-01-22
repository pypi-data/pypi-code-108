import abc
from pyocs.pyocs_interface import UniteInterface
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *


class Aml972Common(UniteInterface):

    def get_board_macro(self):
        # CVT_DEF_BOARD_TYPE
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_PLATFORM_" + board_type + "_SUB_" + sub_board_type + "_CH"
        ret = self.get_macro_line("CVT_DEF_BOARD_TYPE", board_macro)
        return ret

    def get_chip_macro(self):
        # CVT_DEF_CHIP_TYPE
        chip_remark = self.request_dict[self.ocs_demand.chip_remark]
        chip_type_str = self.request_dict[self.ocs_demand.chip_name]
        if 'T972-B' in chip_type_str:
            ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_AMLT972_DDPLUS")
        else:
            ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_AMLT972_NORMAL")
        return ret

    def get_flash_size_macro(self):
        # CVT_DEF_FLASH_SIZE
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_SIZE_" + flash_size
        ret = self.get_macro_line("CVT_DEF_FLASH_SIZE", flash_size_macro)
        return ret

    def get_pwm_macro(self):
        # Pwm占空比宏：[占空比：60]
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        if pwm_macro == '100':
            return ''
        else:
            return self.get_macro_line("CVT_DEF_CURRENT_REF_DUTY", pwm_macro)

    def get_wifi_macro(self):
        demand_str = self.ocs_demand.get_wifi_bluetooth()
        if 'WB8723DU' in demand_str:
            return self.get_macro_line("CVT_DEF_WIFI_TYPE", "ID_WIFI_TYPE_WB8723DU")
        else:
            return self.get_macro_line("CVT_DEF_WIFI_TYPE", "ID_WIFI_TYPE_ATBM6022")

    def get_bluetooth_macro(self):
        demand_str = self.ocs_demand.get_wifi_bluetooth()
        if 'WB8723DU' in demand_str and '蓝牙模块' in demand_str:
            return self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_RTK8761")
        else:
            return ''

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
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('Eshare', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_APP_ESHARE", "1")
        else:
            ret = self.get_macro_line("CVT_EN_APP_ESHARE", "0")
        return ret

    def get_eshare_or_maxhubshare_macro(self):
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('Eshare', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_APP_ESHARE", "1")
        elif other_app_list and other_app_list.rfind('MAXHUB Share', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_APP_CVTE_MAXHUB_SHARE", "1")
        else:
            ret = ''
        return ret
        
    def get_ddr_macro(self):
        ret = ''
        ddr_str = self.ocs_demand.get_ddr_size()
        if "1G" in ddr_str:
            ret += self.get_macro_line("CVT_DEF_DDR_SIZE", "ID_DDR_1G")
        elif "2G" in ddr_str:
            ret += self.get_macro_line("CVT_DEF_DDR_SIZE", "ID_DDR_2G")
        return ret

    def get_code_branch(self):
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if not region_name_list:
            raise NoRegionError('此单无区域')
        if '中国' == region_name_list:
            self._code_branch = 'dtmb_fae'
        else:
            self._code_branch = 'oversea_fae'
        return self._code_branch

    def get_tuner_macro(self):
        ret = ''
        tuner_type_str = self.request_dict[self.ocs_demand.tuner_name]
        if 'R842' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_TUNER_TYPE", "ID_TUNER_TYPE_RAFAEL_R842")
        elif 'MXL661' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_TUNER_TYPE", "ID_TUNER_TYPE_SILICON_MXL661")
        return ret

    def get_far_filed_voice_macro(self):
        ret = ''
        option_func_str = self.request_dict[self.ocs_demand.option_func]
        if '外挂远场语音模块' in option_func_str or '外挂MIC接口' in option_func_str:
            ret += self.get_macro_line("CVT_EN_FAR_FIELD_VOICE", "TRUE")
        return ret

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass