from projectRule.mtk9632.Mtk9632Common import Mtk9632Common
from customers.customer_common.common_database import commonDataBase

class Ruler(Mtk9632Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = ""

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
        ret += '//ocs ID & board & chip & flash & sound 板卡硬件相关' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        # ret += self.get_ddr_macro()
        ret += self.get_flash_size_macro()
        ret += '//ci' + '\n'
        ret += self.get_ci_macro()
        ret += '//tuner' + '\n'
        ret += self.get_tuner_macro()
        ret += '//logo & ir & keypad 常修改项' + '\n'
        ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_COMMON_DEFAULT")
        ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_CVTE_AM_KA80")
        ret += self.get_macro_line("CVT_DEF_KEYPAD_TYPE", "ID_KEYPAD_CVTE_7KEY_COMMON_DEFAULT")
        # ret += self.get_macro_line("CVT_DEF_KEYPAD_ADC", "ID_KEYPAD_ADC_COMMON_DEFAULT")
        ret += self.get_macro_line("CVT_DEF_PANEL_NAME", "\"General_3840_2160\"")
        ret += '//panel & pq & ref 屏相关的修改项' + '\n'
        if 'fae_9632' in self.get_code_branch():
            ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_GENERAL_3840_2160")
        else:
            ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_GENERAL_1920_1080")
        ret += self.get_pwm_macro()
        ret += self.get_eshare_macro()
        ret += self.get_wifi_macro()
        macro_str = self.ocs_demand.get_wifi_bluetooth()
        if 'WB7638U' in macro_str:
            ret += self.get_macro_line("CVT_EN_BLUETOOTH", "1")
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_MT7638")
        elif 'WB8723DU' in macro_str:
            ret += self.get_macro_line("CVT_EN_BLUETOOTH", "1")
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_RTK8761")
        # 默认打开 CEC ARC
        ret += self.get_macro_line("CVT_EN_CEC", "1")
        ret += self.get_macro_line("CVT_EN_ARC", "1")
        ret += '//menu config & launcher' + '\n'
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and 'GAIA' in other_app_list:
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_TYPE", "ID_LAUNCHER_40_GAIA_20_FALL")
        else:
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_TYPE", "ID_LAUNCHER_40_NON_GAIA_SPACE")

        if other_app_list and 'ZEASN' in other_app_list:
            ret += self.get_macro_line("CVT_EN_APP_ZEASN_SK706", "1")

        if other_app_list and 'Eshare' in other_app_list:
            pass
        if self.get_android_system():
            ret += self.get_ocs_country()

        ret += '// end\n'
        return ret

    def get_android_system(self):
        requirement = self.get_customer_special_requirement()
        if "安卓11" in requirement:
            return "an11"
        return None

    def get_ocs_country(self):
        ret = ''
        db = commonDataBase()
        region_name_str = self.request_dict[self.ocs_demand.region_name]
        if region_name_str != '':
            system = db.get_region_mapping_info_by_country(region_name_str)[0]
            if "ISDB" in system:
                ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_PHILIPPINES")
            else:
                ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_TURKEY")
        return ret














