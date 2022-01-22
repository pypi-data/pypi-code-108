from projectRule.hisi56x.hisi56xCommon import hisi56xCommon
from pyocs import pyocs_confluence
import re

class Ruler(hisi56xCommon):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = ''

    # 测试类型
    _test_type = 'E'

    def get_ocs_modelid(self):
        project_list = self.request_dict[self.ocs_demand.product_name].split('.')
        project = project_list[1] + '_' + project_list[2]
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        kb = pyocs_confluence.PyocsConfluence()
        if (region_name_list == None) or (region_name_list == "") or (region_name_list == "无"):
            region_name_list = '智利'
        country = kb.get_country_name_by_country(region_name_list)
        if not country:
            country = 'CHILE'
        batch_code = self.request_dict[self.ocs_demand.customer_batch_code]
        batch_code = re.sub("\D|'-'", "", batch_code)
        if not batch_code:
            batch_code = '01202001001'
        else:
            batch_code = batch_code.replace('-', '_')
        machine = self.request_dict[self.ocs_demand.customer_machine]
        machine = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", '', machine)
        if not machine:
            machine = 'E55DM0000'
        else:
            machine = machine.replace('.', '_')
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_LC546PU1L01' + '_BLUE_' + batch_code + '_' + machine
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
        ret += '// hardware & charge' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        #ret += self.get_tuner_macro()#56x  ATBM253
        ret += self.get_pwm_macro()
        ret += self.get_maxhubshare_macro()
        ret += '// panel & pq & Logo' + '\n'
        ret += self.get_macro_line("CVT_DEF_PANEL_TYPE", "ID_PNL_General_3840_2160")
        ret += self.get_macro_line("CVT_DEF_PQ_TYPE", "ID_PQ_JPE_DEFAULT")

        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        ret += '// special request' + '\n'
        if 'Gaia AI' in other_app_list:
            ret += self.get_macro_line("CVT_EN_APP_TV_SPEECH_SERVICE", "1")
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        kb = pyocs_confluence.PyocsConfluence()
        #print("region_name_list",region_name_list)
        if (region_name_list == None) or (region_name_list == "") or (region_name_list == "无"):
            region_name_list = '智利'
        country = kb.get_country_name_by_country(region_name_list)
        if not country:
            country = 'CHILE'
        ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", 'ID_COUNTRY_' + country)
        ret += self.get_macro_line("CUSTOMER_MODE", "CUSTOMER_MODE_COMMON_DAICE")
        ret += '// end\n'
        return ret


















