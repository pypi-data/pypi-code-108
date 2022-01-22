import abc
from pyocs.pyocs_interface import UniteInterface


class Msd3683Common(UniteInterface):

    def get_board_macro(self):
        # 主板宏：CVT_DEF_BOARD_TYPE
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        if 'MS3683' == product_split_list[1]:
            main_project = 'MST3683'
        else:
            main_project = 'MST3663B'
        board_type = product_split_list[2]
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_CH_" + sub_board_type
        ret = "#define CVT_DEF_BOARD_TYPE".ljust(self._space) + board_macro + '\n'
        return ret

    def get_chip_macro(self):
        chip_type = self.request_dict[self.ocs_demand.chip_name]
        if 'MSD3683QB-8-00GB(DD)' == chip_type:
            hashkey_type = 'CVT_HASH_KEY_MSD3683QB_8_00GB_AAC_DD'
        elif 'MSD3683QB-8-00GB' == chip_type:
            hashkey_type = 'CVT_HASH_KEY_MSD3683QB_8_00GB_AAC_DD'
        elif 'MSD3683QB(DD,DD+)' == chip_type:
            hashkey_type = 'CVT_HASH_KEY_MSD3683QB_8_00GB_AAC_DDP'
        elif 'MSD3683QTA-8-Z1' == chip_type:
            hashkey_type = 'CVT_HASH_KEY_MSD3683QTA_8_Z1_AAC'
        elif 'MSD3683QTA-8-00G0(DD;DD+)' == chip_type:
            hashkey_type = 'CVT_HASH_KEY_MSD3683QTA_8_00G0_AAC_DDP'
        elif 'MSD3683QB-8-Z1' == chip_type:
            hashkey_type = 'CVT_HASH_KEY_MSD3683QB_Z1_AAC'
        else:
            raise RuntimeError('此芯片型号没有录入，请补充')
        ret = "#define CVT_DEF_HASH_KEY".ljust(self._space) + hashkey_type + '\n'
        return ret

    def get_pwm_macro(self):
        # Pwm占空比宏：[占空比：60]
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        ret = "#define CVT_DEF_CURRENT_REF_DUTY".ljust(self._space) + pwm_macro + '\n'
        return ret

    def get_ci_macro(self):
        # CI PLUS
        ret = ''
        if (not self.request_dict[self.ocs_demand.ci_type]) and (not self.request_dict[self.ocs_demand.ciplus_name]):
            ret = '#define CVT_EN_CI_PLUS'.ljust(self._space) + '0' + '\n'
        elif 'CI_Plus' in self.request_dict[self.ocs_demand.ciplus_name]:
            ret = '#define CVT_EN_CI_PLUS'.ljust(self._space) + '1' + '\n'
        else:
            ret = '#define CVT_EN_CI_PLUS'.ljust(self._space) + '0' + '\n'
        return ret

    def get_code_branch(self):
        return self._code_branch

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

