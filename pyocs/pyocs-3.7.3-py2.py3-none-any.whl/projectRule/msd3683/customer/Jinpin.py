from projectRule.msd3683.Msd3683Common import Msd3683Common
from pyocs import pyocs_confluence
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(Msd3683Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN_NEW'

    # 代码分支
    _code_branch = ''

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
        machine = self.request_dict[self.ocs_demand.customer_machine]
        machine = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", '', machine)
        if not machine:
            machine = 'X00XX0000'
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
        _space = 60
        ret += '#elif ( IsModelID('+ self.get_ocs_modelid() + ') )' + '\n'
        ret += '// ocs' + '\n'
        ret += '#define CVT_DEF_MANTIS_OCS_ID'.ljust(_space) + '"CP' + self.ocs_number + '"' + '\n'
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_ci_macro()
        ret += self.get_pwm_macro()

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_PVR_EU_RS22_R81_22309W_0001' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_JPE_BLUE_1366' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel & pq' + '\n'
        ret += '#define CVT_DEF_PANEL_NAME'.ljust(_space) + '"PT320AT01_5"' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_General_1366_768' + '\n'
        ret += '#define CVT_DEF_PQ_TYPE'.ljust(_space) + 'ID_PQ_JPE_PT320AT01_5_CP467206' + '\n'

        ret += '// language & region' + '\n'
        ret += '#define CVT_EN_LANG_ENGLISH'.ljust(_space) + '1' + '\n'
        ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'LANGUAGE_ENGLISH' + '\n'
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
        ret += ('#define CVT_EN_COUNTRY_' + country).ljust(_space) + '1' + '\n'
        ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'OSD_COUNTRY_' + country + '\n'

        ret += '// special request' + '\n'

        ret += '// end\n'
        return ret

    def get_code_branch(self):
        if self.ocs_demand.get_region_name() == "美国" or self.ocs_demand.get_region_name() == "韩国":
            self._code_branch = 'r01'
        else:
            self._code_branch = '3683_r02'
        return self._code_branch
