from projectRule.mtk5522.Mtk5522Common import Mtk5522Common
from pyocs import pyocs_confluence
import re
from customers.customer_common.common_database import commonDataBase

class Ruler(Mtk5522Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = 'fae'

    # 测试类型
    _test_type = 'E'

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
        machine = self.request_dict[self.ocs_demand.customer_machine]
        machine = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", '', machine)
        if not machine:
            machine = 'X00XX0000'
        else:
            machine = machine.replace('.', '_')
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_LSC550FN19_W' + '_JPE_' + batch_code + '_' + machine
        return modelid

    def get_ocs_require(self):
        """获取ocs上的配置，生成配置代码
        Args:
            ocs_number：OCS订单号
        Returns:
             返回配置代码
        """
        ret = ''
        ret += '#elif ( IsModelID('+ self.get_ocs_modelid() + ') )' + '\n'
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_ddr_macro()
        ret += self.get_wifi_macro()
        ret += self.get_ci_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_macro()
        ret += self.get_tuner_type_macro()

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(self._space) + 'ID_IR_JP_IPTV_AP_RS41_81_41638W_0034' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(self._space) + 'ID_LOGO_JINPIN_JPE' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel id' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE '.ljust(self._space) + 'ID_PNL_General_4K2K_VB1_DUAL_PORT' + '\n'
        ret += '#define CVT_DEF_PQ_TYPE'.ljust(self._space) + 'ID_PQ_JINPIN_DEFAULT_LSC550FN19_W' + '\n'

        ret += '// brand id' + '\n'
        ret += '#define CUSTOMER_MODE'.ljust(self._space) + 'CUSTOMER_MODE_COMMON' + '\n'

        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]

        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'DUBAI'
        elif 'CONGO_KINSHASA' in country:
            country = 'CONGO_DEMOCRATIC'

        if 'DUBAI' == country:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(self._space) + 'ID_COUNTRY_UNITED_ARAB_EMIRATES' + '\n'
        else:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(self._space) + 'ID_COUNTRY_' + country + '\n'
        if chip_type in self.dvb_chip:
            if country == 'COLOMBIA' or country == 'PANAMA':
                ret += '#define CVT_DEF_MARKET_REGION'.ljust(self._space) + 'ID_MARKET_REGION_EU_DVBT_COL' + '\n'
            else:
                ret += '#define CVT_DEF_MARKET_REGION'.ljust(self._space) + 'ID_MARKET_REGION_EU_DVBT' + '\n'
        elif chip_type in self.isdb_chip:
            ret += '#define CVT_DEF_MARKET_REGION'.ljust(self._space) + 'ID_MARKET_REGION_SA_ISDB' + '\n'
        else:
            raise RuntimeError('此芯片型号没有录入，请添加适配该区域的相关配置，请处理')

        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and 'Gaia 2.0' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(self._space) + 'ID_LAUNCHER_JINPIN_GAIA_20' + '\n'
        elif other_app_list and 'Gaia AI' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(self._space) + 'ID_LAUNCHER_JINPIN_GAIA_20_AI' + '\n'
        elif other_app_list and 'Gaia 1.0' in other_app_list:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(self._space) + 'ID_LAUNCHER_30_GAIA_10' + '\n'
        else:
            ret += '#define CVT_DEF_LAUNCHER_TYPE'.ljust(self._space) + 'ID_LAUNCHER_20_STARK_OS' + '\n'

        ret += '// end\n'
        return ret


















