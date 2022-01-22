from projectRule.mtk9632.Mtk9632Common import Mtk9632Common
import re
from customers.customer_common.common_database import commonDataBase


class Ruler(Mtk9632Common):

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
        elif any(tn in tuner_type_str for tn in ['EDU-12908INPRA','EDU-12908INPRC','EDU-12908INPRD']):
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

    def get_tv_system(self):
        ret = ''
        tv_system_str = self.request_dict[self.ocs_demand.tv_system]
        if 'ATV' in tv_system_str and 'DVB' not in tv_system_str:
            ret += self.get_macro_line("CVT_EN_ONLY_ATV_SOURCE", "1")
        return ret

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
        ret += self.get_ddr_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_ci_macro()
        ret += self.get_tuner_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_or_maxhubshare_macro()
        ret += self.get_tv_system()

        if 'fae_9632_an11' in self.get_code_branch():
            macro_str = self.ocs_demand.get_wifi_bluetooth()
            other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
            if 'WB7638U' in macro_str:
                ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_TYPE", "ID_CUSTOMER_BUILD_IN_BLUETOOTH")
                if 'Gaia AI' in other_app_list:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH_VOICE")
                else:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH")
            elif 'WB8723DU' in macro_str:
                ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_TYPE", "ID_CUSTOMER_HANG_OUT_BLUETOOTH")
                if 'Gaia AI' in other_app_list:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH_VOICE")
                else:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH")

            ret += '// ir & keypad & logo' + '\n'
            ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_JP_IPTV_AP_81_53338W_0003")
            ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_JPE_BLUE")
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_SKIN_LOGO", "ID_LAUNCHER_SKIN_LOGO_NONE")
            ret += '// panel id' + '\n'
            ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_GENERAL_3840_2160_2Division")
            ret += self.get_macro_line("CVT_DEF_PQ_TYPE", "ID_PQ_JPE_COMMON")
            ret += '// customer' + '\n'
            if any(ct in self.get_ocs_country() for ct in \
                   ['PANAMA', 'COLOMBIA', 'PHILIPPINES', 'FRENCH_GUIANA', 'GUYANA', 'DOMINICAN', 'PERU', ]):
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_PANAMA_DAICE")
            elif any(ct in self.get_ocs_country() for ct in ['CHILE', 'JAMAICA', 'URUGUAY', 'PERU', 'COSTA_RICA', 'VENEZUELA']):
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_CHILE_DAICE")
            else:
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_UAE_DAICE")
            ret += '// end\n'

        elif 'fae_9632' in self.get_code_branch():
            macro_str = self.ocs_demand.get_wifi_bluetooth()
            other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
            if 'WB7638U' in macro_str:
                ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_TYPE", "ID_CUSTOMER_BUILD_IN_BLUETOOTH")
                if 'Gaia AI' in other_app_list:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH_VOICE")
                else:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH")
            elif 'WB8723DU' in macro_str:
                ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_TYPE", "ID_CUSTOMER_HANG_OUT_BLUETOOTH")
                if 'Gaia AI' in other_app_list:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH_VOICE")
                else:
                    ret += self.get_macro_line("CVT_DEF_JPE_BLUETOOTH_CONFIG", "ID_CUSTOMER_BLUETOOTH")

            ret += '// ir & keypad & logo' + '\n'
            ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_JP_IPTV_AP_81_53338W_0003")
            ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_JPE_BLUE_48")
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_SKIN_LOGO", "ID_LAUNCHER_SKIN_LOGO_NONE")
            ret += '// panel id' + '\n'
            ret += self.get_macro_line("CVT_DEF_JPE_PANEL_CONFIG", "ID_CUSTOMER_PANEL_T650QVR09_4")
            ret += '// customer' + '\n'
            if any(ct in self.get_ocs_country() for ct in \
                   ['PANAMA', 'JAMAICA', 'COLOMBIA', 'PHILIPPINES', 'FRENCH_GUIANA', 'GUYANA', 'DOMINICAN', 'PERU',\
                    'VENEZUELA']):
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_PANAMA_DAICE")
            else:
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_DUBAI_DAICE")
            ret += '// end\n'

        elif 'fae_6681' in self.get_code_branch():
            macro_str = self.ocs_demand.get_wifi_bluetooth()
            other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
            if 'WB8723DU' in macro_str:
                if 'Gaia AI' in other_app_list:
                    ret += self.get_macro_line("CVT_EN_APP_TV_SPEECH_SERVICE", "1")
                else:
                    ret += self.get_macro_line("CVT_EN_BLUETOOTH_ON_BOARD", "1")
            ret += '// ir & keypad & logo' + '\n'
            ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_JP_IPTV_AP_81_53338W_0003")
            ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_JPE_BLUE_48")
            ret += self.get_macro_line("CVT_DEF_LAUNCHER_SKIN_LOGO", "ID_LAUNCHER_SKIN_LOGO_NONE")
            ret += '// panel id' + '\n'
            ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_GENERAL_1920_1080")
            ret += self.get_macro_line("CVT_DEF_PQ_TYPE", "ID_PQ_JPE_COMMON")
            ret += '// customer' + '\n'
            if any(ct in self.get_ocs_country() for ct in \
                   ['PANAMA', 'JAMAICA', 'COLOMBIA', 'PHILIPPINES', 'FRENCH_GUIANA', 'GUYANA', 'DOMINICAN', 'PERU',\
                    'VENEZUELA']):
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_PANAMA_DAICE")
            else:
                ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_DUBAI_DAICE")
            ret += '// end\n'
        return ret

    def get_ocs_country(self):
        ret = ''
        db = commonDataBase()
        region_name_str = self.request_dict[self.ocs_demand.region_name]
        if region_name_str != '':
            country = db.get_region_mapping_info_by_country(region_name_str)[3]
            # 国家补丁
            if country == None:
                country = 'DUBAI'
            ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_" + country)
        return ret


















