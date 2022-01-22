import abc
from pyocs.pyocs_interface import UniteInterface
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *


class hisi56xCommon(UniteInterface):

    def get_board_macro(self):
        # CVT_DEF_BOARD_TYPE
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_TP_SK702_" + board_type + "_SUB_" + sub_board_type
        ret = self.get_macro_line("CVT_DEF_BOARD_TYPE", board_macro)
        return ret

    def get_chip_macro(self):
        # CVT_DEF_CHIP_TYPE
        chip_remark = self.request_dict[self.ocs_demand.chip_remark]
        chip_type_str = self.request_dict[self.ocs_demand.chip_name]
        ddr_size = self.request_dict[self.ocs_demand.ddr_name]
        if ddr_size == None :
            ddr_size = str(ddr_size)
        if 'V5630D0N' in chip_type_str:
            ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_V5630D0N")
        elif 'V5630N0N' in chip_type_str:
            ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_V5630N0N")
        elif 'V5600N0N' in chip_type_str:
            if '512M' in ddr_size :
                ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_V5600N0N_EXTER_512M")
            elif '1G' in ddr_size :
                ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_V5600N0N_EXTER_1G")
        elif 'V5600D0N' in chip_type_str:
            if '512M' in ddr_size :
                ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_V5600D0N_EXTER_512M")
            elif '1G' in ddr_size :
                ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", "ID_CHIP_V5600D0N_EXTER_1G")
        return ret

    def get_ddr_size(self):
        ddr_size = self.request_dict[self.ocs_demand.ddr_name]
        print("ddr_size",ddr_size)
        


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
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('Eshare', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_APP_ESHARE", "1")
        else:
            ret = self.get_macro_line("CVT_EN_APP_ESHARE", "0")
        return ret

    def get_maxhubshare_macro(self):
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('MAXHUB Share', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_APP_MAXHUB_SCREENSHARE", "1")
        else:
            ret = self.get_macro_line("CVT_EN_APP_MAXHUB_SCREENSHARE", "0")
        return ret


    def get_code_branch(self):
        return 'fae_56x_isdb'


    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass