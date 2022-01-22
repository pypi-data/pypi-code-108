from projectRule.hisi530.hisi530Common import Hisi530Common


class Ruler(Hisi530Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = 'spc080_fae'

    # 测试类型
    _test_type = 'F'

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        modelid = 'CP' + self.ocs_number + '_SAMPLE_' + project + '_ID_PNL_GENERAL_4K_2K' \
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
        ret += self.get_btsc_macro()
        ret += self.get_dolby_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_ddr_macro()
        ret += self.get_pwm_macro()
        # ret += self.get_ci_macro()
        ret += self.get_eshare_macro()
        # ret += self.get_wifi_macro()

        # 因为对于样品订单来说不需要关注遥控器/按键板/logo等的配置项，如果写客户订单的处理逻辑，需要注意这些配置项
        ret += '//ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_CVTE_AM_KA80' + '\n'
        ret += '#define CVT_DEF_KEYPAD_TYPE'.ljust(_space) + 'ID_KEYPAD_CVTE_DEFAULT' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_COMMON_DEFAULT' + '\n'

        # 样品订单不需要关注屏幕信息，如果写客户订单的处理逻辑，需要注意
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_General_3840_2160' + '\n'
        ret += '#define CVT_DEF_SOUND_TYPE'.ljust(_space) + 'ID_SOUND_TPA3110_COMMON_DEFAULT_12V8R8W' + '\n'

        ret += '// language & country' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if region_name_list == "中国":
            ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_CHINESE_CN' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'COUNTRY_DUBAI' + '\n'
        else:
            ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'COUNTRY_CHINA' + '\n'

        ret += '// region & vod $ launcher & xml' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if region_name_list == "中国":
            ret += '#define CVT_DEF_APPS_GROUP'.ljust(_space) + 'ID_APPS_DTMB' + '\n'
            ret += '#define CVT_DEF_VOD_TYPE'.ljust(_space) + 'ID_VOD_GITV' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_FIGHTER' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_30_SKIN'.ljust(_space) + 'ID_LAUNCHER_30_SKIN_QIYI' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_30_POSTERS'.ljust(_space) + 'ID_LAUNCHER_30_POSTERS_FIGHTER' + '\n'
            ret += '#define CVT_EN_ALI_TV'.ljust(_space) + '1' + '\n'
        else:
            ret += '#define CVT_DEF_APPS_GROUP'.ljust(_space) + 'ID_APPS_DEFAULT' + '\n'
            ret += '#define CVT_DEF_VOD_TYPE'.ljust(_space) + 'ID_VOD_NONE' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_NEBULA' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_30_SKIN'.ljust(_space) + 'ID_LAUNCHER_30_SKIN_FALL' + '\n'
        ret += '#define CVT_DEF_CUSTOMER_CONFIG'.ljust(_space) + 'ID_MENU_CFG_XML_CVTE_DEFAULT' + '\n'

        ret += '// special request' + '\n'

        ret += '//END\n'
        return ret


















