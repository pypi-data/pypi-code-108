from projectRule.mtk5510.Mtk5510Common import Mtk5510Common
from customers.customer_common.common_database import commonDataBase
from pyocs import pyocs_confluence
import re

class Ruler(Mtk5510Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = ''

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
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_PT320AT01_1' + '_JPE_' + batch_code + '_' + machine
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
        ret += self.get_ddr_macro()
        ret += self.get_wifi_macro()
        ret += self.get_ci_macro()
        ret += self.get_tuner_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_macro()

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        if self._code_branch == 'fae_eu':
            ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_IPTV_AP_RS41_81_41638W_0034' + '\n'
        elif self._code_branch == 'fae_sa':
            ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_AP_81_53338W_0033' + '\n'
        elif self._code_branch == 'fae_us':
            ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_IPTV_AM_81_53338W_0024' + '\n'
        else:
            raise RuntimeError('不支持此区域，请确认，谢谢！')
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_JPE_RED_CHAR_BLUE_BACKGROUND' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel & pq' + '\n'
        ret += '#define CVT_DEF_PANEL_NAME'.ljust(_space) + '"PT320AT01_1"' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE '.ljust(_space) + 'ID_PNL_General_1366_768' + '\n'
        ret += '#define CVT_DEF_PQ_TYPE'.ljust(_space) + 'ID_PQ_COMMON_DEFAULT' + '\n'

        ret += '// language & country & region' + '\n'
        ret += '#define CVT_DEF_LANG_GROUP_TYPE'.ljust(_space) + 'ID_JPE_CONF_LANG_DEFAULT' + '\n'
        ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'DUBAI'
        if 'DUBAI' == country:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(self._space) + 'ID_COUNTRY_UNITED_ARAB_EMIRATES' + '\n'
        else:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(self._space) + 'ID_COUNTRY_' + country + '\n'
        if self._code_branch == 'fae_eu':
            ret += '#define CVT_DEF_JINPIN_CUSTOMER_CONFIG'.ljust(_space) + 'CONFIG_JINPIN_DVBT' + '\n'
            ret += '#define CVT_DEF_MENU_CONFIG_XML_TYPE'.ljust(_space) + 'ID_MENU_CONFIG_XML_COMMON_JINPIN_EU_FOR_GAIA' + '\n'
        elif self._code_branch == 'fae_sa':
            ret += '#define CVT_DEF_JINPIN_CUSTOMER_CONFIG'.ljust(_space) + 'CONFIG_JINPIN_ISDB' + '\n'
            ret += '#define CVT_DEF_MENU_CONFIG_XML_TYPE'.ljust(_space) + 'ID_MENU_CONFIG_XML_COMMON_JINPIN_ISDB_NOPVR_GAIA_NO_GOOGLE_PLAY' + '\n'
        elif self._code_branch == 'fae_us':
            ret += '#define CVT_DEF_JINPIN_CUSTOMER_CONFIG'.ljust(_space) + 'CONFIG_JINPIN_ATSC' + '\n'
            ret += '#define CVT_DEF_MENU_CONFIG_XML_TYPE'.ljust(_space) + 'ID_MENU_CONFIG_XML_COMMON_JINPIN_US' + '\n'
        else:
            raise RuntimeError('不支持此区域，请确认，谢谢！')

        ret += '// launcher' + '\n'
        # GAIA
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if 'Gaia 2.0' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_JINPIN' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_BATCH_CODE'.ljust(_space) + '"B994QhdQSm48RtsV"' + '\n'
        elif 'Gaia 1.0' in other_app_list:
            ret += '#define CVT_EN_APP_GAIA_10'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_GAIA_10' + '\n'
        elif 'Gaia AI' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_JINPIN' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_BATCH_CODE'.ljust(_space) + '"B994QhdQSm48RtsV"' + '\n'
            ret += '#define CVT_EN_CONFIG_JINPIN_GAIA_AI_LAUNCHER'.ljust(_space) + 'TRUE' + '\n'
        else:
            raise RuntimeError('no this GAIA type')
        ret += '#define CVT_DEF_LAUNCHER_SKIN_TYPE'.ljust(_space) + 'ID_LAUNCHER_SKIN_30_JINPIN_COMMON_NO_LOGO' + '\n'

        ret += '// special request' + '\n'

        """
        ret += '// auto check' + '\n'
        batch_code_name = self.request_dict[self.ocs_demand.customer_batch_code]
        batch_code_name = re.sub("\D|'-'", "", batch_code_name)
        batch_code_name_list = list(batch_code_name)
        batch_code_name_list.insert(2, '-')
        batch_code_name_list.insert(9, '-')
        batch_code_name = ''.join(batch_code_name_list)
        ret += '//' + '#define CVT_JPE_PRODUCT_ID'.ljust(_space) + '"' + batch_code_name + '"' + '\n'
        ret += '//' + '#define CVT_DEF_CUSTOMER_INFO_SW_CHECK_ID'.ljust(_space) + '"' + '评审单号' + ' ' + batch_code_name + '"' + '\n'
        ret += '//' + '#define CVT_DEF_CUSTOMER_INFO_CHECK'.ljust(_space) + '1' + '\n'
        """

        ret += '// end\n'
        return ret

