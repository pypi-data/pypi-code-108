from projectRule.mtk5522.Mtk5522Common import Mtk5522Common


class Ruler(Mtk5522Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = 'fae'

    # 测试类型
    _test_type = 'F'

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        modelid = 'CP' + self.ocs_number + '_YAGYAN_' + project + '_ID_PNL_GENERAL_4K_2K' \
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
        ret += self.get_tuner_type_macro()

        # 因为对于样品订单来说不需要关注遥控器/按键板/logo等的配置项，如果写客户订单的处理逻辑，需要注意这些配置项
        ret += '//ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_CVTE_KA84' + '\n'
        ret += '#define CVT_DEF_KEYPAD_TYPE'.ljust(_space) + 'ID_KEYPAD_CVTE_DEFAULT' + '\n'
        ret += '#define CVT_DEF_KEYPAD_ADC'.ljust(_space) + 'ID_KEYPADADC_CVTE1SAR' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_CVTE_DEFAULT' + '\n'

        # 样品订单不需要关注屏幕信息，如果写客户订单的处理逻辑，需要注意
        ret += '#define CVT_DEF_PANEL'.ljust(_space) + 'CVT_PANEL_GENERAL_4K2K_VB1' + '\n'

        ret += '//国家 & 语言' + '\n'
        ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'

        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]

        if chip_type in self.dvb_chip:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'ID_COUNTRY_HUNGARY' + '\n'
            ret += '#define CVT_DEF_MARKET_REGION'.ljust(_space) + 'ID_MARKET_REGION_EU_DVBT' + '\n'
        elif chip_type in self.isdb_chip:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'ID_COUNTRY_CHILE' + '\n'
            ret += '#define CVT_DEF_MARKET_REGION'.ljust(_space) + 'ID_MARKET_REGION_SA_ISDB' + '\n'
        else:
            raise RuntimeError('此芯片型号没有录入，请处理')

        ret += '// special request' + '\n'
        ret += '#define CVT_DEF_MENU_CONFIG_XML_TYPE'.ljust(_space) + 'ID_MENU_CONFIG_XML_MX_DEFAULT_EU' + '\n'

        # GAIA
        other_app_str = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_str and 'Gaia 2.0' in other_app_str:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(self._space) + 'ID_LAUNCHER_30_GAIA_20' + '\n'
        elif other_app_str and 'Gaia AI' in other_app_str:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(self._space) + 'ID_LAUNCHER_30_GAIA_20_AI' + '\n'
        elif other_app_str and 'Gaia 1.0' in other_app_str:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(self._space) + 'ID_LAUNCHER_30_GAIA_10' + '\n'
        else:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_20_STARK_OS' + '\n'

        ret += '//END\n'
        return ret


















