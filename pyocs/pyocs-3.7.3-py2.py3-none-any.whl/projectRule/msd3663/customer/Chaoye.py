from projectRule.msd3663.Msd3663Common import Msd3663Common
from pyocs import pyocs_confluence
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(Msd3663Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_JINPIN_NEW'

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
                country = 'NONE'
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
        modelid = 'CP' + self.ocs_number + '_JPE_' + project + '_' + country + '_LC000PNL000' + '_BLUE_' + batch_code + '_' + machine
        return modelid

    def get_ocs_require(self):
        """获取ocs上的配置，生成配置代码
        Args:
            ocs_number：OCS订单号
        Returns:
             返回配置代码
        """
        ret = ''
        _space = 52
        ret += '#elif ( IsModelID('+ self.get_ocs_modelid() + ') )' + '\n'
        ret += '// ocs' + '\n'
        ret += self.get_macro_line('CVT_DEF_MANTIS_OCS_ID', '"CP' + self.ocs_number + '"')
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_dvd_macro()
        ret += self.get_tuner_macro()
        ret += self.get_ci_macro()
        ret += self.get_pwm_macro()

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & logo' + '\n'
        ret += self.get_macro_line('CVT_DEF_IR_TYPE', 'ID_IR_JP_PVR_EU_RS22_R81_22309W_0001')
        ret += self.get_macro_line('CVT_DEF_LOGO_TYPE', 'ID_LOGO_JPE_BLUE_1366')

        # 金品代测订单不需要关注PANEL
        ret += '// panel & pq' + '\n'
        ret += self.get_macro_line('CVT_DEF_PANEL_TYPE', 'ID_PNL_General_1366_768')
        ret += self.get_macro_line('CVT_DEF_PQ_TYPE', 'ID_PQ_JPE_PT320AT01_5_CP467206')

        # 制式区分
        ret += '// special request' + '\n'
        if any(ct in self.get_ocs_country() for ct in ['PANAMA', 'JAMAICA','COLOMBIA']):
            ret += self.get_macro_line('CVT_DEF_JPE_BRAND_CONFIG', 'CONFIG_JPE_BRAND_PANAMA_DAICE')
        else:
            ret += self.get_macro_line('CVT_DEF_JPE_BRAND_CONFIG', 'CONFIG_JPE_BRAND_UAE_DAICE')
        ret += '// end\n'
        return ret

    def get_ocs_country(self):
        ret = ''
        db = commonDataBase()
        region_name_str = self.request_dict[self.ocs_demand.region_name]
        if region_name_str != '':
            country = db.get_region_mapping_info_by_country(region_name_str)[2]
            # 国家补丁
            if country == None:
                country = 'UAE'
                product = self.request_dict[self.ocs_demand.product_name].split('.')[1]
                if 'MS3663' == product:
                    country = 'PANAMA'
            ret += self.get_macro_line('CVT_DEF_COUNTRY_SELECT', 'OSD_COUNTRY_' + country)
            ret += self.get_macro_line('CVT_EN_COUNTRY_' + country, '1')
        return ret
