from projectRule.rda8503.rda8503Common import Rda8503Common
import re

class Ruler(Rda8503Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = 'trunk'

    # 测试类型
    _test_type = 'E'

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
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
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_NIGERIA_T390XVN02_0' + '_BLUE_' + batch_code + '_' + machine
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
        ret += '// hardware' + '\n'
        # 主板宏
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        # 客户特殊需求
        ret += self.get_dc_voltage_detect_macro()
        ret += self.get_dc_voltage_low_value_macro()
        # Pwm占空比宏：[占空比：60]
        ret += self.get_pwm_macro()

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_AP_81_41V59W_1004' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_JINPIN_BLUE_1366' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel & pq & sound' + '\n'
        panel_info_name = 'T390XVN02_0'
        ret += '#define CVT_DEF_PANEL_INFO_NAME'.ljust(_space) + '"' + panel_info_name + '"' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_JPE_T390XVN02_0' + '\n'
        ret += '#define CVT_DEF_PQ_GROUP_TYPE'.ljust(_space) + 'JPE_CONF_PQ_T390XVN02_0_CP441715' + '\n'

        ret += '// language' + '\n'
        ret += '#define CVT_EN_LANG_ENGLISH'.ljust(_space) + '1' + '\n'
        ret += '#define CVT_DEF_LANGUAGE'.ljust(_space) + 'APP_OSDLANG_ENGLISH' + '\n'

        ret += '// special request' + '\n'

        ret += '// end\n'
        return ret


















