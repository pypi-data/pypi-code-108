import abc
from pyocs.pyocs_interface import UniteInterface


class Hisi553Common(UniteInterface):

    def get_board_macro(self):
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[0] + "_" + product_split_list[1].rstrip('S')
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BOARD_" + main_project + "_" + board_type + "_SUB_" + sub_board_type
        ret = "#define CVT_DEF_BOARD_TYPE".ljust(self._space) + board_macro + '\n'
        return ret

    def get_chip_macro(self):
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        if 'V553' in chip_type:
            chip_type = 'V553'
        elif 'V620' in chip_type:
            chip_type = 'V620'
        else:
            raise RuntimeError('此芯片型号没有录入，请补充')
        chip_macro = "ID_CHIP_" + chip_type
        ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + chip_macro + '\n'
        return ret

    def get_dolby_macro(self):
        enable_dolby = ''
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        if 'D00' in chip_type:
            enable_dolby = '1'
        elif 'N00' in chip_type:
            enable_dolby = '0'
        else:
            raise RuntimeError('此芯片型号没有录入，请补充')
        ret = "#define CVT_EN_DOLBYPLUS".ljust(self._space) + enable_dolby + '\n'
        return ret

    def get_flash_size_macro(self):
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_" + flash_size
        ret = "#define CVT_DEF_FLASH_SIZE".ljust(self._space) + flash_size_macro + '\n'
        return ret

    def get_pwm_macro(self):
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        ret = "#define CVT_DEF_CURRENT_REF_DUTY".ljust(self._space) + pwm_macro + '\n'
        return ret

    def get_eshare_macro(self):
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and other_app_list.rfind('Eshare', 0, len(other_app_list)-1) != -1:
            ret = '#define CVT_EN_APK_ESHARE'.ljust(self._space) + '1' + '\n'
        else:
            ret = '#define CVT_EN_APK_ESHARE'.ljust(self._space) + '0' + '\n'
        return ret

    def get_wifi_bluetooth_macro(self):
        ret = ''
        wifi_bluetooth_type_str = self.ocs_demand.get_choose_wifi()
        if 'RTL8723' in wifi_bluetooth_type_str:
            ret = '#define CVT_DEF_BLUETOOTH_TPYE'.ljust(self._space) + 'ID_BLUETOOTH_TYPE_RTK8723' + '\n'
        return ret

    def get_code_branch(self):
        return self._code_branch

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

