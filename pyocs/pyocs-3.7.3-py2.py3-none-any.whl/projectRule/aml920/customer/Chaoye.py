from projectRule.aml920.Aml920Common import Aml920Common
from pyocs import pyocs_confluence
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(Aml920Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN_ATV'

    # 代码分支
    _code_branch = 'fae_global'

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
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_LC546PU1L01' + '_JPE_' + batch_code + '_' + machine
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
        ret += self.get_ddr_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_tuner_macro()
        ret += self.get_pwm_macro()
        ret += self.get_wifi_macro()
        ret += '// ir & logo' + '\n'
        ret += self.get_macro_line("CVT_DEF_IR_TYPE", "ID_IR_JP_IPTV_AP_RS41_81_41628W_0033")
        ret += self.get_macro_line("CVT_DEF_LOGO_TYPE", "ID_LOGO_JPE_BLUE")
        ret += '// panel & pq' + '\n'
        ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_FAC_1366X768")
        ret += self.get_macro_line("CVT_DEF_PQ_TYPE", "ID_PQ_JPE_COMMON_DEFAULT")
        ret += '// language & country & region' + '\n'
        ret += self.get_macro_line("CUSTOMER_LANG_GROUP", "ID_CUSTOMER_LANG_GROUP_COMMON")
        ret += self.get_macro_line("CVT_DEF_LANGUAGE_SELECT", "ID_LANGUAGE_ENGLISH_US")
        ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_DUBAI")
        ret += '// special request' + '\n'
        ret += self.get_macro_line("CVT_DEF_CUSTOMER_TYPE", "JPE_CONF_COMMON_DEFAULT")
        ret += '// end\n'
        return ret


















