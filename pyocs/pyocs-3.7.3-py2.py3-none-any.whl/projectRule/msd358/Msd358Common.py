import abc
from pyocs.pyocs_interface import UniteInterface


class Msd358Common(UniteInterface):

    def get_board_macro(self):
        # 主板宏：CVT_DEF_BOARD_TYPE
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[1].rstrip('S')
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "BD_SUB_TP_" + main_project + "_" + board_type + "_" + sub_board_type
        ret = "#define CVT_DEF_BOARD_TYPE".ljust(self._space) + board_macro + '\n'
        return ret

    def get_chip_macro(self):
        # 主芯片宏：CVT_DEF_CHIP_TYPE
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0].replace('-', '_')
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
        ret = "#define CVT_DEF_CURRENT_REF_DUTY".ljust(self._space) + pwm_macro + '\n'
        return ret

    def get_eshare_macro(self):
        # ESHARE
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('Eshare', 0, len(other_app_list)-1) != -1:
            ret = '#define CVT_EN_APP_ESHARE'.ljust(self._space) + '1' + '\n'
        else:
            ret = '#define CVT_EN_APP_ESHARE'.ljust(self._space) + '0' + '\n'
        return ret

    def get_tv_system_macro(self):
        # tv system is defined by tuner type
        ret = ''
        tuner_str = self.request_dict[self.ocs_demand.tuner_name]
        if 'F螺纹头' in tuner_str:
            ret = '#define CVT_DEF_DTV_SYSTEM_TYPE'.ljust(self._space) + 'ID_DTV_SYSTEM_ISDB//ntsc' + '\n'
        return ret

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

