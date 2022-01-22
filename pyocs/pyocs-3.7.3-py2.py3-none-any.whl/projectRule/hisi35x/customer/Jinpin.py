from projectRule.hisi35x.hisi35xCommon import hisi35xCommon
from pyocs import pyocs_confluence
import re
from customers.customer_common.common_database import commonDataBase


class Ruler(hisi35xCommon):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = 'fae_ap'

    # 测试类型
    _test_type = 'E'

    _country_setting_space='        '

    def get_wifi_bluetooth_macro(self):
        ret = ''
        wifi_bluetooth_type_str = self.ocs_demand.get_wifi_bluetooth()
        if 'SKI.WB8723DU.2' in wifi_bluetooth_type_str:
            ret += self.get_macro_line("CVT_EN_BT_ON_BOARD", "1")
            ret += self.get_macro_line("CVT_DEF_BLUETOOTH_TYPE", "ID_BLUETOOTH_TYPE_RTK8761")
        return ret

    def check_if_only_atv(self):
        ret = False
        atv_list = self.request_dict[self.ocs_demand.chip_remark]
        if '纯模拟' in atv_list:
            ret = True
        else:
            ret = False
        return ret

    def check_if_tuner_ntsc(self):
        ret = False
        tuner_type_str = self.request_dict[self.ocs_demand.tuner_name]
        print("tuner_type_str",tuner_type_str)
        if 'R842（F螺纹头）' in tuner_type_str:
            ret = True
        else:
            ret = False
        return ret

    def get_code_branch(self):
        tv_system_str = self.request_dict[self.ocs_demand.tv_system]
        if "ATV/ISDB" == tv_system_str :
            self._code_branch = 'fae_sa'
        else:
            self._code_branch = 'fae_eu'
        return self._code_branch

    def get_ocs_modelid(self):
        project_list = self.request_dict[self.ocs_demand.product_name].split('.')
        project = project_list[1] + '_' + project_list[2]
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'LIBYA'
        batch_code = self.request_dict[self.ocs_demand.customer_batch_code]
        batch_code = re.sub("\D|'-'", "", batch_code)
        if not batch_code:
            batch_code = '01201901001'
        else:
            batch_code = batch_code.replace('-', '_')
        machine = self.request_dict[self.ocs_demand.customer_machine]
        machine = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", '', machine)
        if not machine:
            machine = 'E55DM0000'
        else:
            machine = machine.replace('.', '_')
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_PT320AT01_5' + '_BLUE_' + batch_code + '_' + machine
        return modelid

    def get_ocs_require(self):
        """获取ocs上的配置，生成配置代码
        Args:
            ocs_number：OCS订单号
        Returns:
             返回配置代码
        """
        ret = ''
        ret += '#elif ( IsModelID(' + self.get_ocs_modelid() + ') )' + '\n'
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        branch = self.get_code_branch()
        if 'fae_eu' == branch:
            ret += self.get_tuner_macro()
        ret += self.get_pwm_macro()
        ret += self.get_ci_macro()
        macro_str = self.ocs_demand.get_ci_plus()
        if 'CI_Plus' in macro_str:
            ret += self.get_macro_line("CVT_EN_CI_FUNC", "1")
            ret += self.get_macro_line("CVT_DEF_CI_PLUS_TYPE", "ID_CI_PLUS_TYPE_CI_PLUS")
        ret += self.get_eshare_macro()
        ret += self.get_wifi_bluetooth_macro()

        ret += '// ir & keypad & logo' + '\n'
        if 'fae_ap' == branch:
            ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_JP_IPTV_AP_81_53338W_0003")
            ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_TYPE_JPE_BLUE_BB_36")

        ret += '// panel & pq' + '\n'
        ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_General_1366_768")
        if 'fae_ap' == branch:
            ret += self.get_macro_line("CVT_DEF_PQ_TYPE", "ID_PQ_JPE_PT320AT01_5_CS509538")

        ret += '// customer' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'UNKNOW'
        ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(self._space) + self._country_setting_space + 'ID_COUNTRY_' + country + '\n'
        tv_system_str = self.request_dict[self.ocs_demand.tv_system]
        if ("ATV" == tv_system_str) or (self.check_if_only_atv()):
            if 'fae_sa' != branch:
                ret += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_ATV_ONLY")
        if self.check_if_tuner_ntsc() and (self.check_if_only_atv()):
            if 'fae_sa' != branch:
                ret += self.get_macro_line("CVT_EN_NTSC_ATV", "1")
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if 'Gaia AI' in other_app_list:
            ret += self.get_macro_line("CVT_EN_APP_TV_SPEECH_SERVICE", "1")
        ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_COMMON")
        ret += '// end\n'
        return ret


















