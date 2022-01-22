from projectRule.msd3663.Msd3663Common import Msd3663Common
from pyocs import pyocs_confluence
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(Msd3663Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_MINGCAI'

    # 代码分支
    _code_branch = 'fae_dvb'

    # 测试类型
    _test_type = 'E'


    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        if 'MS3663' == product_split_list[1]:
            if not country:
                country = 'PANAMA'
        else:
            if not country:
                country = 'VIETNAM'
        batch_code = self.request_dict[self.ocs_demand.customer_batch_code]
        batch_code = re.sub("\D|'-'", "", batch_code)
        if not batch_code:
            batch_code = '01000001001'
        else:
            batch_code = batch_code.replace('-', '_')
        modelid = 'CP' + self.ocs_number + '_MC_' + batch_code + '_' + project + '_' + country + '_PT320AT01_5_MCB_03_BLACK'
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
        ret += '// ocs ID & board & sound' + '\n'
        ret += '#define CVT_DEF_MANTIS_OCS_ID'.ljust(_space) + '"CP' + self.ocs_number + '"' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_dvd_macro()
        ret += self.get_tuner_macro()
        ret += self.get_ci_macro()
        ret += self.get_flash_size_macro()


        # 明彩代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// logo & ir & keypad' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_MC_BLACK' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_MC_IPTV_AP_MCB_03_007F' + '\n'
        ret += '#define CVT_DEF_KEYPAD_TYPE'.ljust(_space) + 'KEYPAD_CVT_DEFAULT' + '\n'

        # 明彩代测订单不需要关注PANEL
        ret += '// panel & pq' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_General_1366_768' + '\n'
        ret += self.get_pwm_macro()
        ret += '#define CVT_DEF_BACKLIGHT_VALUE'.ljust(_space) + '100' + '\n'

        ret += '// language & country' + '\n'
        ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'LANGUAGE_ENGLISH' + '\n'
        ret += '#define CVT_DEF_LANGUAGE_GROUP_TYPE'.ljust(_space) + 'CVT_CONF_LANG_EURO_6' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        if 'MS3663' == product_split_list[1]:
            if not country:
                country = 'PANAMA'
        else:
            if not country:
                country = 'VIETNAM'
            elif 'DUBAI' == country:
                country = 'UNITED_ARAB_EMIRATES'
        ret += ('#define CVT_EN_COUNTRY_' + country).ljust(_space) + '1' + '\n'
        ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'OSD_COUNTRY_' + country + '\n'

        ret += '// special request' + '\n'

        ret += '// end\n'
        return ret
