import abc
from pyocs.pyocs_interface import UniteInterface


class V56Common(UniteInterface):

    def get_board_macro(self):
        # 主板宏：CVT_DEF_BOARD_TYPE
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[1].rstrip('S')
        if 'V56' == main_project:
            main_project = 'VST56'
        board_type = product_split_list[2]
        board_str = self.request_dict[self.ocs_demand.title_name]
        if 'PA671C' in board_str:
            board_type = 'PA671C'
        if 'SK108' == main_project:
            board_type = board_type + '_V53RW'
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_CH_" + sub_board_type
        ret = "#define CVT_DEF_BOARD_TYPE".ljust(self._space) + board_macro + '\n'
        return ret

    def get_chip_macro(self):
        # 主芯片宏：CVT_DEF_CHIPSET
        chip_type = self.request_dict[self.ocs_demand.chip_name]
        if 'TSUMV56RUU-Z1' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RUU_Z1' + '\n'
        elif 'TSUMV56RUE-Z1' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RUE_Z1' + '\n'
        elif 'TSUMV56RBUT-Z1' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RBUT_Z1' + '\n'
        elif 'TSUMV56RBET-Z1' == chip_type or 'TSUMV56RBET-0051' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RBET_Z1' + '\n'
        elif 'TSUV56RJUL-Z1' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUV56RJUL_Z1' + '\n'
        elif 'TSUMV56RUU' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RUU' + '\n'
        elif 'TSUMV56RUU(DD)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RUU' + '\n'
        elif 'TSUMV56RUE(DD)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RUE' + '\n'
        elif 'TSUMV56RBUT(DD)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RBUT' + '\n'
        elif 'TSUMV56RBET(DD)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RBET' + '\n'
        elif 'TSUMV56RUU-0068(RMVB)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV56RUU_0068' + '\n'
        elif 'TSUMV53RWUT(DD)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV53RWUT' + '\n'
        elif 'TSUMV53RWUT-Z1' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV53RWUT_Z1' + '\n'
        elif 'TSUMV53RWU(DD)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV53RWU' + '\n'
        elif 'TSUMV53RWU-Z1' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV53RWU_Z1' + '\n'
        elif 'TSUMV53RWET(DD)' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV53RWET' + '\n'
        elif 'TSUMV53RWET-Z1' == chip_type:
            ret = "#define CVT_DEF_CHIPSET".ljust(self._space) + 'CVT_TSUMV53RWET_Z1' + '\n'
        else:
            raise RuntimeError('此芯片型号没有录入，请补充')
        return ret

    def get_pwm_macro(self):
        # Pwm占空比宏：[占空比：60]
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        ret = "#define CVT_DEF_CURRENT_REF_DUTY".ljust(self._space) + pwm_macro + '\n'
        return ret

    def get_code_branch(self):
        return self._code_branch

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

