from projectRule.v56.V56Common import V56Common
from pyocs import pyocs_confluence
import re

class Ruler(V56Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_CHAOYE'

    # 代码分支
    _code_branch = 'r01'

    # 测试类型
    _test_type = 'E'


    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        batch_code = self.request_dict[self.ocs_demand.customer_batch_code]
        batch_code = re.sub("\D|'-'", "", batch_code)
        if not batch_code:
            batch_code = '01000001001'
        else:
            batch_code = batch_code.replace('-', '_')
        machine = self.request_dict[self.ocs_demand.customer_machine]
        machine = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", '', machine)
        if not machine:
            machine = 'X00XX0000'
        else:
            machine = machine.replace('.', '_')
        modelid = 'CP' + self.ocs_number + '_CY_' + project + '_LC000PNL000' + '_BLUE_' + batch_code + '_' + machine
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
        ret += '// board & chip & Flash & pwm' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_pwm_macro()

        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_AP_RS22_CN_EXIT' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_JINPIN_BLUE_1366' + '\n'

        ret += '// panel id' + '\n'
        ret += '#define CVT_DEF_JPE_PANEL_CONFIG'.ljust(_space) + 'CONFIG_JPE_PANEL_PT320AT02_2_CP573653' + '\n'

        ret += '// brand id' + '\n'
        ret += '#define CVT_DEF_JPE_BRAND_CONFIG'.ljust(_space) + 'CONFIG_JPE_BRAND_COMMON' + '\n'

        ret += '// end\n'
        return ret
