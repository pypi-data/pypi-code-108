from projectRule.hisi35x.hisi35xCommon import hisi35xCommon
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *

class Ruler(hisi35xCommon):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_PYOCS_AUTO'

    # 代码分支
    _code_branch = ''

    # 测试类型
    _test_type = 'F'

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        modelid = 'CS' + self.ocs_number + '_SAMPLE_' + project + '_ID_PNL_GENERAL_1920_1080' \
                  + '_DUTY_' + self.request_dict[self.ocs_demand.pwm_name]
        return modelid

    def get_ocs_require(self):
        """获取ocs上的配置，生成配置代码
        Args:
            ocs_number：OCS订单号
        Returns:
             返回配置代码
        """
        ret = ''
        _space = 60
        ret += '#elif ( IsModelID(' + self.get_ocs_modelid() + ') )' + '\n'
        ret += '// hardware item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_tuner_macro()
        ret += self.get_wifi_bluetooth_macro()
        ret += self.get_pwm_macro()
        ret += self.get_ci_macro()
        macro_str = self.ocs_demand.get_ci_plus()
        if 'CI_Plus' in macro_str:
            ret += self.get_macro_line("CVT_EN_CI_FUNC", "1")
            ret += self.get_macro_line("CVT_DEF_CI_PLUS_TYPE", "ID_CI_PLUS_TYPE_CI_PLUS")

        ret += '// charge item' + '\n'
        ret += self.get_eshare_macro()

        ret += '// region item' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if not region_name_list:
            raise NoRegionError('此单无区域')

        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        main_project = product_split_list[0] + "_" + product_split_list[1]

        if 'TP_SK508' == main_project or 'T_SK508' == main_project:
            if region_name_list == "中国":
                ret += self.get_macro_line("CVT_DEF_LANGUAGE_SELECT", "ID_LANGUAGE_CHINESE_CN")
                ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_CHINA")
            else:
                ret += self.get_macro_line("CVT_DEF_LANGUAGE_SELECT", "ID_LANGUAGE_ENGLISH_US")
                ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_DUBAI")
            ret += self.get_atv_macro()

        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if 'Gaia 2.0' in other_app_list:
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_TYPE", "ID_LAUNCHER_40_GAIA_20_FALL")
        else:
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_TYPE", "ID_LAUNCHER_40_NON_GAIA_SPACE")

        ret += '// end\n'
        return ret


















