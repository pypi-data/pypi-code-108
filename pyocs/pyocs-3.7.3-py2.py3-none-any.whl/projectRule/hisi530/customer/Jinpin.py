from projectRule.hisi530.hisi530Common import Hisi530Common
from pyocs import pyocs_confluence
import re
from customers.customer_common.common_database import commonDataBase

class Ruler(Hisi530Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN_OVERSEA'

    # 代码分支
    _code_branch = '530fae'

    # 测试类型
    _test_type = 'E'

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'DUBAI'
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
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_LSC490FN11_W' + '_STAR_TRACK_' + batch_code + '_' + machine
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
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_btsc_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_ddr_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_macro()
        wifi_type_str = ''
        if not self.request_dict[self.ocs_demand.wifi_bluetooth_type]:
            if not self.request_dict[self.ocs_demand.wifi_module_info]:
                wifi_type_str = self.request_dict[self.ocs_demand.wifi_module_info]
        else:
            wifi_type_str = self.request_dict[self.ocs_demand.wifi_bluetooth_type]

        """
        if wifi_type_str.rfind('M06USA1', 0, len(wifi_type_str)-1) != -1:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(_space) + 'ID_WIFI_TYPE_MT7601U' + '\n'
        elif wifi_type_str.rfind('M603USA1', 0, len(wifi_type_str)-1) != -1:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(_space) + 'ID_WIFI_TYPE_MT7603U' + '\n'
        # CI PLUS
        if (not self.request_dict[self.ocs_demand.ci_type]) and self.request_dict[self.ocs_demand.ciplus_name] == '无':
            pass
        elif self.request_dict[self.ocs_demand.ciplus_name] == 'CI_Plus （CVTE）':
            ret += '#define CVT_DEF_CI_TYPE'.ljust(_space) + 'ID_CI_TYPE_CI_PLUS' + '\n'
        elif self.request_dict[self.ocs_demand.ci_type] == "CI":
            ret += '#define CVT_DEF_CI_TYPE'.ljust(_space) + 'ID_CI_TYPE_CI' + '\n'
        """

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_IPTV_AP_RS41_81_41628W_0033' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_TYPE_JINPIN_STAR_TRACK' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel & pq' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_LC546PU1L01_MTC_3840_2160' + '\n'
        ret += '#define CVT_DEF_PQ_TYPE'.ljust(_space) + 'ID_PQ_TYPE_JINGPING_LSC490FN13_W_CP372661' + '\n'

        ret += '// language & country & region' + '\n'
        ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'DUBAI'
        ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'ID_COUNTRY_' + country + '\n'

        ret += '// special request' + '\n'
        ret += '#define CVT_DEF_CUSTOMER_CONFIG'.ljust(_space) + 'CONFIG_JPE_OVERSEA_HIDE_GOOGLE_STOER' + '\n'

        ret += '// end\n'
        return ret


















