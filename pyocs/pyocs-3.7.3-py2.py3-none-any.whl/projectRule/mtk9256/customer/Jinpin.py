from projectRule.mtk9256.Mtk9256Common import Mtk9256Common
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(Mtk9256Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = ""

    # 测试类型
    _test_type = 'F'

    def get_flash_size_macro(self):
        # Flash Size宏：ID_FLASH_SIZE_[Flash Size：8G]
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        if flash_size == '8G':
            ret = ''
        else:
            flash_size_macro = "ID_FLASH_SIZE_" + flash_size
            ret = self.get_macro_line("CVT_DEF_FLASH_SIZE", flash_size_macro)
        return ret

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
            country = 'NONE'
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
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_LC000PNL000' + '_BLUE_' + batch_code + '_' + machine
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
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_ci_macro()
        ret += self.get_tuner_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_or_maxhubshare_macro()
        macro_str = self.ocs_demand.get_wifi_bluetooth()
        if 'WB7638U' in macro_str:
            ret += self.get_macro_line("CVT_EN_BLUETOOTH", "1")
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_MT7638")
        elif 'WB8723DU' in macro_str:
            ret += self.get_macro_line("CVT_EN_BLUETOOTH", "1")
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_RTK8723")
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if 'GAIA AI' in other_app_list.upper():
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_TYPE", "ID_LAUNCHER_40_GAIA_AI_JPE_2020")
        ret += '// ir & keypad & logo' + '\n'
        ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_JP_PVR_AP_81_86708W_0003")
        ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_JPE_JPE_WR")
        ret += self.get_macro_line("CVT_DEF_LAUNCHER_SKIN_LOGO", "ID_LAUNCHER_SKIN_LOGO_NONE")
        ret += '// panel id' + '\n'
        ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_GENERAL_1920_1080")
        ret += self.get_macro_line("CVT_DEF_PQ_TYPE", "ID_PQ_JPE_COMMON")
        ret += '// brand id' + '\n'
        if "fae_sa" in self.get_code_branch():
            ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_CHILE_DAICE")
        elif "fae_us" in self.get_code_branch():
            ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_MEXICO_DAICE")
        elif "fae_eu" in self.get_code_branch():
            if any(ct in self.get_ocs_country() for ct in \
                   ['PANAMA', 'COLOMBIA', 'FRENCH_GUIANA', 'GUYANA', 'DOMINICAN' ]):
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_PANAMA_DAICE")
            else:
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_UAE_DAICE")
        ret += '// end\n'
        return ret

    def get_ocs_country(self):
        ret = ''
        branch = self.get_code_branch()
        if "fae_sa" in branch:
            ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_PHILIPPINES")
        elif "fae_us" in branch:
            ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_MEXICO")
        else:
            ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_TURKEY")
        return ret
















