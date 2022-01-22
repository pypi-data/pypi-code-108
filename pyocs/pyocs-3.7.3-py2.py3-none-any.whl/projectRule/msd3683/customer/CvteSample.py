from projectRule.msd3683.Msd3683Common import Msd3683Common
from pyocs import pyocs_confluence
import re

class Ruler(Msd3683Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = ''

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
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_ci_macro()
        ret += self.get_pwm_macro()

        ret += '// special' + '\n'

        ret += '// end\n'
        return ret

    def get_code_branch(self):
        if self.ocs_demand.get_region_name() == "美国" or self.ocs_demand.get_region_name() == "韩国":
            self._code_branch = 'r01'
        else:
            self._code_branch = '3683_r02'
        return self._code_branch
