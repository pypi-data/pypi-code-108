from projectRule.aml972.Aml972Common import Aml972Common


class Ruler(Aml972Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_PYOCS_AUTO'

    # 代码分支
    _code_branch = ''

    # 测试类型
    _test_type = 'F'

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        modelid = 'CS' + self.ocs_number + '_SAMPLE_' + project + '_ID_PNL_GENERAL' \
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
        ret += '// hardware item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_ddr_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_pwm_macro()
        ret += self.get_wifi_macro()
        ret += self.get_bluetooth_macro()
        ret += self.get_far_filed_voice_macro()
        ret += '// charge item' + '\n'
        ret += self.get_eshare_macro()
        ret += '// end\n'
        return ret

















