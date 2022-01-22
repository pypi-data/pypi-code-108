from projectRule.hisi553.hisi553Common import Hisi553Common
from pyocs import pyocs_confluence
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(Hisi553Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = 'spc080_fae'

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
        ret += self.get_flash_size_macro()
        ret += self.get_dolby_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_macro()
        ret += self.get_wifi_bluetooth_macro()
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

        # 金品代测订单不需要关注IR/LOGO等的配置项
        ret += '// ir & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_IPTV_AP_RS41_81_41628W_0033' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_TYPE_JINPIN_JPE' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel & pq' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_General_3840_2160_2Division' + '\n'
        ret += '#define CVT_DEF_PQ_TYPE'.ljust(_space) + 'ID_PQ_JINPIN_V553_LC546PU1L01' + '\n'

        ret += '// language & country & region' + '\n'
        brand_str = self.request_dict[self.ocs_demand.customer_batch_code]
        # 语言组
        if '哈尼' in brand_str:
            ret += '#define CVT_DEF_JPE_LANGUAGE_GROUP'.ljust(_space) + 'CONFIG_JPE_LANG_GRP_ENFRARRUFADETR' + '\n'
        elif '星光电器' in brand_str:
            ret += '#define CVT_DEF_JPE_LANGUAGE_GROUP'.ljust(_space) + 'CONFIG_JPE_LANG_GRP_ENFRARRUFAPT' + '\n'
        elif '升贸' in brand_str or '锐欧' in brand_str:
            ret += '#define CVT_DEF_JPE_LANGUAGE_GROUP'.ljust(_space) + 'CONFIG_JPE_LANG_GRP_ENFRARFA' + '\n'
        elif '大雄' in brand_str:
            ret += '#define CVT_DEF_JPE_LANGUAGE_GROUP'.ljust(_space) + 'CONFIG_JPE_LANG_GRP_ENFRARRUFAIW' + '\n'
        else:
            ret += '#define CVT_DEF_JPE_LANGUAGE_GROUP'.ljust(_space) + 'CONFIG_JPE_LANG_GRP_COMMON' + '\n'
        ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'DUBAI'
        ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'COUNTRY_' + country + '\n'

        ret += '// launcher & menu config' + '\n'
        # GAIA
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if 'Gaia 2.0' in other_app_list:
            ret += '//#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_GAIA_20_JUMPIN' + '\n'
            ret += '//#define CVT_DEF_LAUNCHER_30_SKIN'.ljust(_space) + 'ID_LAUNCHER_30_SKIN_APT_JUMPIN' + '\n'
        elif 'Gaia AI' in other_app_list:
            ret += '//#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_GAIA_20_JUMPIN' + '\n'
            ret += '#define CVT_EN_APP_SPOTIFY_TV'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_EN_APP_TV_SPEECH'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_DEF_SMART_IR_KEYLAYOUT'.ljust(_space) + 'ID_KEYLAYOUT_SQY_GAIA20' + '\n'
            ret += '//#define CVT_DEF_LAUNCHER_30_SKIN'.ljust(_space) + 'ID_LAUNCHER_30_SKIN_APT_JUMPIN' + '\n'
        else:
            ret += '//#define CVT_DEF_LAUNCHER_TYPE'.ljust(_space) + 'ID_LAUNCHER_30_FALL' + '\n'
            ret += '//#define CVT_DEF_LAUNCHER_30_SKIN'.ljust(_space) + 'ID_LAUNCHER_30_SKIN_FALL' + '\n'

        ret += '// special request' + '\n'
        ret += '#define CVT_DEF_JPE_BRAND_CONFIG'.ljust(_space) + 'CONFIG_JPE_BRAND_INTEX_NONE' + '\n'

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


















