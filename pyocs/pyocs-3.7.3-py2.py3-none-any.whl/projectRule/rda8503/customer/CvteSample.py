from projectRule.rda8503.rda8503Common import Rda8503Common


class Ruler(Rda8503Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = 'trunk'

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
        ret += '#elif ( IsModelID(' + self.get_ocs_modelid() + ') )' + '\n'
        ret += '// board & chip & Flash & pwm' + '\n'
        # 主板宏
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        # 客户特殊需求
        ret += self.get_dc_voltage_detect_macro()
        ret += self.get_dc_voltage_low_value_macro()
        # Pwm占空比宏：[占空比：60]
        ret += self.get_pwm_macro()

        # 样品订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_CVT_K80' + '\n'
        ret += '#define CVT_DEF_KEYPAD_TYPE'.ljust(_space) + 'KEYPAD_SEQUNCE_CVT_DEFAULT' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_CVTE_INITIALIZING' + '\n'

        # 样品订单不需要关注PANEL
        ret += '// panel & pq & sound' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_GENERAL_1366_768' + '\n'

        ret += '// language' + '\n'
        ret += '#define CVT_EN_LANG_ENGLISH'.ljust(_space) + '1' + '\n'
        ret += '#define CVT_DEF_LANGUAGE'.ljust(_space) + 'APP_OSDLANG_ENGLISH' + '\n'

        ret += '// special request' + '\n'

        ret += '// end\n'
        return ret


















