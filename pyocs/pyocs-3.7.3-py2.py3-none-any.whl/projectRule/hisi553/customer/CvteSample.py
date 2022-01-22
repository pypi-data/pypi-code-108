from projectRule.hisi553.hisi553Common import Hisi553Common


class Ruler(Hisi553Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = 'spc080_fae'

    # 测试类型
    _test_type = 'F'

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        modelid = 'CS' + self.ocs_number + '_SAMPLE_' + project + '_ID_PNL_GENERAL_4K_2K' \
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
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_dolby_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_pwm_macro()
        # ret += self.get_ci_macro()
        ret += self.get_eshare_macro()
        ret += self.get_wifi_bluetooth_macro()

        ret += '// language & country' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if region_name_list == "中国":
            ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_CHINESE_CN' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'COUNTRY_CHINA' + '\n'
        else:
            ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'COUNTRY_DUBAI' + '\n'

        ret += '// region & vod $ launcher & xml' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if region_name_list != "中国":
            other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
            if 'Gaia AI' in other_app_list:
                ret += '#define CVT_EN_APP_SPOTIFY_TV'.ljust(_space) + '1' + '\n'
                ret += '#define CVT_EN_APP_TV_SPEECH'.ljust(_space) + '1' + '\n'
                ret += '#define CVT_DEF_SMART_IR_KEYLAYOUT'.ljust(_space) + 'ID_KEYLAYOUT_SQY_GAIA20' + '\n'

        ret += '// end\n'
        return ret


















