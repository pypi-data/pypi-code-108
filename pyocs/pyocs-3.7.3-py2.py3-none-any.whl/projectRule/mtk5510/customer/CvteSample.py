from projectRule.mtk5510.Mtk5510Common import Mtk5510Common


class Ruler(Mtk5510Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

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
        ret += '// board & chip & Flash & pwm' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_pwm_macro()
        ret += self.get_ci_macro()
        ret += self.get_eshare_macro()
        ret += self.get_wifi_macro()
        ret += self.get_ddr_macro()
        ret += self.get_tuner_macro()
        ret += '// country ' + '\n'
        if 'fae_eu' in self.get_code_branch():
            ret +=  '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'ID_COUNTRY_TURKEY' + '\n'

        ret += '// special request' + '\n'
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if 'Gaia 2.0' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_GAIA_20' + '\n'
        elif 'Gaia 1.0' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_GAIA_10' + '\n'
        elif 'Gaia AI' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_GAIA_20_AI' + '\n'

        ret += '// end\n'
        return ret

















