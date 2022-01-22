from projectRule.mt9255.MT9255Common import MT9255Common
from pyocs import pyocs_confluence
from customers.customer_common.common_database import commonDataBase
import re

class Ruler(MT9255Common):

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
        _space = 60
        ret += '#elif ( IsModelID('+ self.get_ocs_modelid() + ') )' + '\n'
        ret += '// hardware & toll item' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_tv_system_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_pwm_macro()
        ret += self.get_maxhub_share_macro()

        # 金品代测订单不需要关注IR/KEYPAD/LOGO等的配置项
        ret += '// ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_JP_IPTV_AP_RS41_81_41628W_0033' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_JPE_BLUE' + '\n'
        ret += '#define CVT_DEF_LAUNCHER_SKIN_LOGO'.ljust(_space) + 'ID_LAUNCHER_SKIN_LOGO_NONE' + '\n'

        # 金品代测订单不需要关注PANEL
        ret += '// panel id' + '\n'
        ret += '#define CVT_DEF_PANEL_TYPE '.ljust(_space) + 'ID_PNL_GENERAL_1366_768' + '\n'
        ret += '#define CVT_DEF_PQ_TYPE '.ljust(_space) + 'ID_PQ_JPE_DEFAULT' + '\n'
        ret += '// brand id' + '\n'
        # 不需要识别NTSC,代码已经做好绑定
        if any(ct in self.get_ocs_country() for ct in \
               ['PANAMA', 'JAMAICA', 'COLOMBIA', 'PHILIPPINES', 'FRENCH_GUIANA', 'GUYANA', 'DOMINICAN', 'PERU', \
                'URUGUAY','VENEZUELA','PARAGUAY','ARGENTINA','HONDURAS','MEXICO','TRINIDAD_AND_TOBAGO','HAITI']):
            ret += '#define CUSTOMER_MODE'.ljust(_space) + 'CUSTOMER_MODE_JAMAICA_DAICE' + '\n'
        else:
            ret += '#define CUSTOMER_MODE'.ljust(_space) + 'CUSTOMER_MODE_DUBAI_DAICE' + '\n'
        ret += '// end\n'
        return ret

    def get_code_branch(self):
        self._code_branch = 'fae_all'
        return self._code_branch

    def get_android_system(self):
        return self._android_system

    def get_ocs_country(self):
        ret = ''
        db = commonDataBase()
        region_name_str = self.request_dict[self.ocs_demand.region_name]
        if region_name_str != '':
            country = db.get_region_mapping_info_by_country(region_name_str)[2]
            # 国家补丁
            if country == None:
                country = 'DUBAI'
            ret += self.get_macro_line("CVT_DEF_COUNTRY_SELECT", "ID_COUNTRY_" + country)
        return ret
