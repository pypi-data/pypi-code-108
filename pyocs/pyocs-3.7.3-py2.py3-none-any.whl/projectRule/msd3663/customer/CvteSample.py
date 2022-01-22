from projectRule.msd3663.Msd3663Common import Msd3663Common
from pyocs import pyocs_confluence
import re

class Ruler(Msd3663Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = 'fae_dvb'

    # 测试类型
    _test_type = 'F'


    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        modelid = 'CP' + self.ocs_number + '_SAMPLE_' + project + '_ID_PNL_GENERAL_1366_768' \
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
        ret += '#elif ( IsModelID('+ self.get_ocs_modelid() + ') )' + '\n'
        ret += '// ocs' + '\n'
        ret += '#define CVT_DEF_MANTIS_OCS_ID'.ljust(_space) + '"CP' + self.ocs_number + '"' + '\n'
        ret += '// board & chip & Flash & pwm' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_dvd_macro()
        ret += self.get_tuner_macro()
        ret += self.get_ci_macro()
        ret += self.get_pwm_macro()

        # 样品订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_CVT_K35' + '\n'
        ret += '#define CVT_DEF_KEYPAD_TYPE'.ljust(_space) + 'KEYPAD_CVT_DEFAULT' + '\n'

        # 样品订单不需要关注PANEL
        ret += '// panel & pq' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_General_1366_768' + '\n'

        ret += '// language & region' + '\n'
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        if 'MS3663' == product_split_list[1]:
            ret += '#define CVT_DEF_ZUI_STRINGS_BIN'.ljust(_space) + 'ZUI_STRINGS_BIN_GU_CAIXUN_COL_COLUMBIA' + '\n'
            ret += '#define CVT_EN_CHECK_COLOMBIA_STRING'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_EN_COUNTRY_PANAMA'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'OSD_COUNTRY_PANAMA' + '\n'
        else:
            ret += '#define CVT_EN_COUNTRY_GEORGIA'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'OSD_COUNTRY_GEORGIA' + '\n'

        ret += '// special' + '\n'

        ret += '// end\n'
        return ret
