import abc
from pyocs.pyocs_interface import UniteInterface
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *


class Mtk9632Common(UniteInterface):

    def get_board_macro(self):
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        if "安卓11" in self.get_customer_special_requirement():
            main_project = product_split_list[1]
        else:
            main_project = product_split_list[0] + "_" + product_split_list[1]
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        if board_type == 'PC822':
            board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_" + sub_board_type + "_CH"
        else:
            board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_" + sub_board_type
        ret = self.get_macro_line("CVT_DEF_BOARD_TYPE", board_macro)
        return ret

    def get_chip_macro(self):
        # 主芯片宏：CVT_DEF_CHIP_TYPE ID_CHIP_[芯片名：MT5510ZHOJ]
        chip_remark = self.request_dict[self.ocs_demand.chip_remark]
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        #print(chip_type)
        chip_type = chip_type.replace("-", "_")
        chip_macro = "ID_CHIP_" + chip_type
        ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", chip_macro)
        return ret

    def get_flash_size_macro(self):
        # Flash Size宏：ID_FLASH_SIZE_[Flash Size：8G]
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_SIZE_" + flash_size
        ret = self.get_macro_line("CVT_DEF_FLASH_SIZE", flash_size_macro)
        return ret

    def get_pwm_macro(self):
        # Pwm占空比宏：[占空比：60]
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        return self.get_macro_line("CVT_DEF_CURRENT_REF_DUTY", pwm_macro)

    def get_wifi_macro(self):
        demand_str = self.ocs_demand.get_wifi_bluetooth()
        if "安卓11" in self.get_customer_special_requirement():
            return self.get_macro_line("CVT_DEF_WIFI_TYPE", "ID_WIFI_TYPE_INTERNAL")
        if 'WB7638U' in demand_str:
            return self.get_macro_line("CVT_DEF_WIFI_TYPE", "ID_WIFI_TYPE_WB7638U")
        else:
            return self.get_macro_line("CVT_DEF_WIFI_TYPE", "ID_WIFI_TYPE_W6022")

    def get_bluetooth_macro(self):
        demand_str = self.ocs_demand.get_wifi_bluetooth()
        if 'WB7638U' in demand_str:
            return self.get_macro_line("CVT_EN_BLUETOOTH", "1")
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
            ret = self.get_macro_line("CVT_EN_APPLIST_ESHARE_SERVICE", '1')
        else:
            ret = ''
        return ret

    def get_eshare_or_maxhubshare_macro(self):
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('Eshare', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_APPLIST_ESHARE_SERVICE", "1")
        elif other_app_list and other_app_list.rfind('MAXHUB Share', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_MAXHUB_SCREEN_SHARE", "1")
        else:
            ret = ''
        return ret
        
    def get_ddr_macro(self):
        ret = ''
        ddr_str = self.ocs_demand.get_ddr_size()
        if ddr_str == '':
            ret += self.get_macro_line("CVT_DEF_DDR_SIZE", "ID_DDR_1P5G")
        return ret

    def get_code_branch(self):
        tv_project = self.ocs_demand.get_ocs_project_name()
        if "SK706" in tv_project:
            self._code_branch = "fae_9632"
        elif "MT9632" in tv_project:
            if "安卓11" in self.get_customer_special_requirement():
                self._code_branch = "fae_9632_an11"
            else:
                self._code_branch = "fae_9632"
        elif "MS6681" in tv_project:
            self._code_branch = "fae_6681"
        elif "SK506" in tv_project:
            self._code_branch = "fae_6681"
        return self._code_branch

    def get_tuner_macro(self):
        ret = ''
        tuner_type_str = self.request_dict[self.ocs_demand.tuner_name]
        if 'R842' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_FIRST_TUNER_TYPE", "ID_TUNER_R842")
        elif 'EDU-12908INPRA' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_FIRST_TUNER_TYPE", "ID_TUNER_R842_EDU_12908INPRA")
        else:
            ret += self.get_macro_line("CVT_DEF_FIRST_TUNER_TYPE", "ID_TUNER_R842")

        if 'RT710' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710")
        elif 'AV2017' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_AV2017")
        elif 'EDS-11980FNPRE' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710_EDS_11980FNPRE")
        else:
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710")

        return ret

    def get_customer_special_requirement(self):
        return self.request_dict[self.ocs_demand.customer_special_requirement]


    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass