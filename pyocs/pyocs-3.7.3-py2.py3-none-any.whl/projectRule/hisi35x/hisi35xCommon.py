import abc
from pyocs.pyocs_interface import UniteInterface
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *

class hisi35xCommon(UniteInterface):

    def get_board_macro(self):
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[0] + "_" + product_split_list[1]
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_" + sub_board_type
        ret = self.get_macro_line("CVT_DEF_BOARD_TYPE", board_macro)
        return ret

    def get_chip_macro(self):
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        if 'V351' in chip_type:
            chip_type = chip_type[chip_type.index('V351'):(chip_type.index('V351')+8)]
        elif 'V350' in chip_type:
            chip_type = chip_type[chip_type.index('V350'):(chip_type.index('V350')+8)]
        else:
            raise RuntimeError('此芯片型号没有录入，请补充')
        chip_macro = "ID_CHIP_" + chip_type
        ret = self.get_macro_line("CVT_DEF_CHIP_TYPE", chip_macro)
        return ret

    def get_dolby_macro(self):
        enable_dolby = ''
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        if 'D0N' in chip_type:
            enable_dolby = '1'
        elif 'N0N' in chip_type:
            enable_dolby = '0'
        else:
            raise RuntimeError('此芯片型号没有录入，请补充')
        ret = self.get_macro_line("CVT_EN_DOLBYPLUS", enable_dolby)
        return ret

    def get_flash_size_macro(self):
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_" + flash_size
        ret = self.get_macro_line("CVT_DEF_FLASH_SIZE", flash_size_macro)
        return ret

    def get_pwm_macro(self):
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        if pwm_macro == '100':
            return ''
        else:
            return self.get_macro_line("CVT_DEF_CURRENT_REF_DUTY", pwm_macro)

    def get_eshare_macro(self):
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('Eshare', 0, len(other_app_list)-1) != -1:
            ret = self.get_macro_line("CVT_EN_APPLIST_ESHARE", '1')
        else:
            ret = self.get_macro_line("CVT_EN_APPLIST_ESHARE", '0')
        return ret

    def get_ci_macro(self):
        demand_str = self.ocs_demand.get_option_func()
        if 'CI' in demand_str:
            return self.get_macro_line("CVT_EN_CI_FUNC", "1")
        else:
            return ''

    def get_atv_macro(self):
        atv_list = self.request_dict[self.ocs_demand.chip_remark]
        if '纯模拟' in atv_list:
            ret = self.get_macro_line("CVT_DEF_MARKET_REGION", 'ID_MARKET_REGION_ATV_ONLY')
        else:
            ret = self.get_macro_line("CVT_DEF_MARKET_REGION", 'ID_MARKET_REGION_EU_DVBT_DVBC')
        return ret

    def get_tuner_macro(self):
        ret = ''
        tuner_type_str = self.request_dict[self.ocs_demand.tuner_name]
        if 'R842' in tuner_type_str and 'RT710' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_TUNER_TYPE", "ID_TUNER_R842_ON_BOARD")
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710_ON_BOARD")
        elif 'EDU-12908INPRA' in tuner_type_str and 'RT710' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_TUNER_TYPE", "ID_TUNER_R842_EDU_12908INPRA")
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710_ON_BOARD")
        elif 'EDU-12908INPRA' in tuner_type_str and 'EDS-11980FNPRE' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_TUNER_TYPE", "ID_TUNER_R842_EDU_12908INPRA")
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710_EDS_11980FNPRD")
        return ret

    def get_wifi_bluetooth_macro(self):
        ret = ''
        wifi_bluetooth_type_str = self.ocs_demand.get_wifi_bluetooth()
        if 'SKI.WB8723DU.2' in wifi_bluetooth_type_str:
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_RTK8761")
        return ret

    def get_code_branch(self):
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[0] + "_" + product_split_list[1]

        # if '508S' in main_project:
        #     self._code_branch = 'fae_eu'
        # else:
        #     self._code_branch = 'fae_ap'

        self._code_branch = 'fae_eu'
        return self._code_branch

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

