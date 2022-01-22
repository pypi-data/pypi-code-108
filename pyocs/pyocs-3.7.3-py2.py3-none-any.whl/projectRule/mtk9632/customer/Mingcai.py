from projectRule.mtk9632.Mtk9632Common import Mtk9632Common
from pyocs import pyocs_confluence
import re
from customers.customer_common.common_database import commonDataBase

class Ruler(Mtk9632Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_MINGCAI'

    # 代码分支
    _code_branch = ""

    # 测试类型
    _test_type = 'E'

    def get_tuner_macro(self):
        ret = ''
        tuner_type_str = self.request_dict[self.ocs_demand.tuner_name]
        if 'R842' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_FIRST_TUNER_TYPE", "ID_TUNER_R842")
        elif 'EDU-12908INPRA' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_FIRST_TUNER_TYPE", "ID_TUNER_R842_EDU_12908INPRA")
        else:
            ret += self.get_macro_line("CVT_DEF_FIRST_TUNER_TYPE", "ID_TUNER_R842")

        if 'RT710' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710")
        elif 'AV2017' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_AV2017")
        elif 'EDS-11980FNPRE' in tuner_type_str:
            ret += self.get_macro_line("CVT_DEF_SECOND_TUNER_TYPE", "ID_TUNER_RT710_EDS_11980FNPRE")

        return ret
        
    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'DUBAI'
        elif 'CONGO_KINSHASA' in country:
            country = 'CONGO_DEMOCRATIC'
        batch_code = self.request_dict[self.ocs_demand.customer_batch_code]
        batch_code = re.sub("\D|'-'", "", batch_code)
        if not batch_code:
            batch_code = '01000001001'
        else:
            batch_code = batch_code.replace('-', '_')
        modelid = 'CP' + self.ocs_number + '_MC_' + batch_code + '_' + project + '_' + country + '_' + 'CC500PV6D_MCB_03'
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
        ret += '// ocs ID & board & chip & flash & sound' + '\n'
        ret += '#define CVT_DEF_MANTIS_OCS_ID'.ljust(_space+8) + '"CP' + self.ocs_number + '"' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_ddr_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_ci_macro()
        ret += self.get_tuner_macro()
        ret += self.get_eshare_or_maxhubshare_macro()
        ret += self.get_wifi_macro()
        macro_str = self.ocs_demand.get_wifi_bluetooth()
        if 'WB7638U' in macro_str:
            ret += self.get_macro_line("CVT_EN_BLUETOOTH", "1")
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_MT7638")
        elif 'WB8723DU' in macro_str:
            ret += self.get_macro_line("CVT_EN_BLUETOOTH", "1")
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_RTK8761")
        ret += '// keypad & ir& logo' + '\n'
        ret += self.get_macro_line("CVT_DEF_KEYPAD_TYPE", "ID_KEYPAD_CVTE_7KEY_COMMON_DEFAULT")
        ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_MC_IPTV_AP_MCB_03_007F")
        ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_COMMON_DEFAULT")
        ret += '// panel & pq' + '\n'
        ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_GENERAL_3840_2160_2Division")
        ret += self.get_pwm_macro()
        ret += '// language & country' + '\n'
        ret += self.get_macro_line("CVT_DEF_LANGUAGE_SELECT", "ID_LANGUAGE_ENGLISH_US")
        ret += self.get_macro_line("CVT_DEF_LANGUAGE_GROUP_TYPE", "MC_CONF_LANGUAGE_DEFAULT")
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        ret += ('#define CVT_EN_COUNTRY_' + country).ljust(_space+8) + '1' + '\n'
        ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space+8) + 'ID_COUNTRY_' + country + '\n'
        ret += '// customer' + '\n'
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if 'Gaia AI' in other_app_list:
            ret += self.get_macro_line("CVT_EN_APP_TV_SPEECH_SERVICE", "1")
        ret += '// end\n'
        return ret

















