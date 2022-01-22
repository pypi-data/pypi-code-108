from projectRule.aml920.Aml920Common import Aml920Common


class Ruler(Aml920Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_PYOCS_AUTO'

    # 代码分支
    _code_branch = 'fae_global'

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
        ret += self.get_tuner_macro()
        ret += self.get_pwm_macro()
        ret += self.get_wifi_macro()
        ret += '// charge item' + '\n'
        # ret += self.get_ci_macro()
        ret += self.get_eshare_macro()
        ret += '// region item' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if region_name_list == "中国":
            ret += self.get_macro_line("CVT_DEF_LANGUAGE_SELECT", "ID_LANGUAGE_CHINESE_CN")
            ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_CHINA")
        else:
            ret += self.get_macro_line("CVT_DEF_LANGUAGE_SELECT", "ID_LANGUAGE_ENGLISH_US")
            ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_INDIA")

        ret += '// end\n'
        return ret

















