from projectRule.msd358.Msd358Common import Msd358Common
from pyocs import pyocs_confluence
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(Msd358Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN'

    # 代码分支
    _code_branch = ''

    # 测试类型
    _test_type = 'E'

    # 安卓系统
    _android_system = ''

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
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_PT430CT01_1' + '_JPE_' + batch_code + '_' + machine
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
        ret += self.get_tv_system_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_macro()

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_IPTV_AP_RS41_81_41628W_0033' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_TYPE_JINPIN_JPE_JOY_1366' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel id' + '\n'
        ret += '#define CVT_DEF_JPE_PANEL_CONFIG'.ljust(_space) + 'CONFIG_JPE_PANEL_PT430CT02_4_CP511944' + '\n'

        ret += '// brand id' + '\n'
        if self._android_system == self.android_4_4:
            ret += '#define CVT_DEF_JPE_BRAND_CONFIG'.ljust(_space) + 'CONFIG_JPE_BRAND_LSX' + '\n'
        else:
            ret += '#define CVT_DEF_JPE_BRAND_CONFIG'.ljust(_space) + 'CONFIG_JPE_BRAND_COMMON' + '\n'
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        country = map_list[2]
        if not country:
            country = 'DUBAI'
        if 'DUBAI' == country:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(self._space) + 'ID_COUNTRY_ARAB' + '\n'
        else:
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(self._space) + 'ID_COUNTRY_' + country + '\n'
        ret += '// end\n'
        return ret

    def get_code_branch(self):
        if self.ocs_demand.get_region_name() == "中国":
            self._code_branch = 'fae'
        elif self.ocs_demand.get_ddr_size() == '512M':
            self._code_branch = 'oversea'
        elif self.ocs_demand.get_flash_size() == '4G':
            self._code_branch = 'oversea'
        elif self.ocs_demand.get_flash_size() == '8G':
            self._code_branch = 'fae'
        else:
            raise RuntimeError('代码选择不在规则之内')
        return self._code_branch

    def get_android_system(self):
        if self.ocs_demand.get_region_name() == "中国":
            self._android_system = self.android_4_4
        elif self.ocs_demand.get_ddr_size() == '512M':
            self._android_system = self.android_4_4
        elif self.ocs_demand.get_flash_size() == '4G':
            self._android_system = self.android_4_4
        elif self.ocs_demand.get_flash_size() == '8G':
            self._android_system = self.android_8_0
        else:
            raise RuntimeError('代码选择不在规则之内')
        return self._android_system
