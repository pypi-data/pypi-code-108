import abc
from pyocs.pyocs_interface import UniteInterface


class Hisi530Common(UniteInterface):

    def get_board_macro(self):
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[0] + "_" + product_split_list[1].rstrip('S')
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_CH_" + sub_board_type
        ret = "#define CVT_DEF_BOARD_TYPE".ljust(self._space) + board_macro + '\n'
        return ret

    def get_chip_macro(self):
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        if 'V530' in chip_type:
            chip_type = 'V530'
        elif 'V510' in chip_type:
            chip_type = 'V510'
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
            ret = "#define CVT_DEF_DOLBY_TYPE".ljust(self._space) + 'ID_DOLBY_PLUS' + '\n'
        elif 'N00' in chip_type:
            ret = "#define CVT_DEF_DOLBY_TYPE".ljust(self._space) + 'ID_DOLBY_NONE' + '\n'
        else:
            raise RuntimeError('此芯片型号没有录入，请补充')
        return ret

    def get_btsc_macro(self):
        ret = ''
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        if 'N0B' in chip_type:
            ret = "#define CVT_EN_BTSC".ljust(self._space) + '1' + '\n'
        return ret

    def get_flash_size_macro(self):
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_SIZE_" + flash_size
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

    def get_ddr_macro(self):
        ret = ''
        ddr_str = self.ocs_demand.get_ddr_size()
        if "1G" in ddr_str:
            ret = '#define CVT_DEF_DDR_SIZE'.ljust(self._space) + 'ID_DDR_1G' + '\n'
        else:
            ret = '#define CVT_DEF_DDR_SIZE'.ljust(self._space) + 'ID_DDR_768M' + '\n'
        return ret

    def get_code_branch(self):
        return self._code_branch

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

