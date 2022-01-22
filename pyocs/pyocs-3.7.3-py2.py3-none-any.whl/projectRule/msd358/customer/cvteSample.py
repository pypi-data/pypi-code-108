from projectRule.msd358.Msd358Common import Msd358Common
from pyocs.pyocs_exception import *


class Ruler(Msd358Common):

    # Customer_ID
    _customer_id = 'CUSTOMER_SAMPLE_AUTO_CONFIG'

    # 代码分支
    _code_branch = ''

    # 测试类型
    _test_type = 'F'

    # 安卓系统
    _android_system = ''

    def get_ocs_modelid(self):
        project = self.request_dict[self.ocs_demand.product_name].replace('.', '_')
        modelid = 'CS' + self.ocs_number + '_SAMPLE_' + project + '_ID_PNL_GENERAL_1920_1080' \
                  + '_DUTY_' + self.request_dict[self.ocs_demand.pwm_name]
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
        ret += '// board & chip & Flash & pwm' + '\n'
        ret += self.get_board_macro()
        ret += self.get_chip_macro()
        ret += self.get_flash_size_macro()
        ret += self.get_pwm_macro()
        ret += self.get_eshare_macro()

        # 因为对于样品订单来说不需要关注遥控器/按键板/logo等的配置项，如果写客户订单的处理逻辑，需要注意这些配置项
        ret += '//ir & keypad & logo' + '\n'
        ret += '#define CVT_DEF_IR_TYPE'.ljust(_space) + 'ID_IR_CVTE_AM_KA80' + '\n'
        ret += '#define CVT_DEF_KEYPAD_TYPE'.ljust(_space) + 'KEYPAD_CVTE' + '\n'
        ret += '#define CVT_DEF_KEYPAD_ADC'.ljust(_space) + 'ID_KEYPAD_ADC_CVTE1SAR_COMMON_DEFAULT' + '\n'
        ret += '#define CVT_DEF_LOGO_TYPE'.ljust(_space) + 'ID_LOGO_CVTE_DEFAULT' + '\n'

        # 样品订单不需要关注屏幕信息，如果写客户订单的处理逻辑，需要注意
        ret += '#define CVT_DEF_PANEL_TYPE'.ljust(_space) + 'ID_PNL_General_1920_1080' + '\n'

        ret += '//国家 & 语言' + '\n'

        if self._android_system == self.android_8_0:  # 只有8.0导入了GAIA
            ret += '#define CVT_EN_LANG_ENGLISH_US'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'ID_COUNTRY_INDIA' + '\n'
            # GAIA
            other_app_str = self.request_dict[self.ocs_demand.other_app_soft]
            if other_app_str and other_app_str.rfind('Gaia 2.0', 0, len(other_app_str) - 1) != -1:
                ret += '#define CVT_DEF_LAUNCHER_SELECT'.ljust(self._space) + 'ID_LAUNCHER_30_GAIA_20_NYS' + '\n'
            elif other_app_str and other_app_str.rfind('Gaia AI', 0, len(other_app_str) - 1) != -1:
                ret += '#define CVT_EN_APP_CVT_TV_SPEECH'.ljust(self._space) + '1' + '\n'
                ret += '#define CVT_DEF_LAUNCHER_SELECT'.ljust(self._space) + 'ID_LAUNCHER_30_GAIA_20_NYS' + '\n'
            elif other_app_str and other_app_str.rfind('Gaia 1.0', 0, len(other_app_str) - 1) != -1:
                ret += '#define CVT_DEF_LAUNCHER_SELECT'.ljust(self._space) + 'ID_LAUNCHER_30_GAIA_10_OVERSEA_FALL' + '\n'
            else:
                ret += '#define CVT_DEF_LAUNCHER_SELECT'.ljust(_space) + 'ID_LAUNCHER_30_NON_GAIA_SPACE' + '\n'
        elif self._android_system == self.android_4_4 and self._code_branch == 'oversea':
            ret += '#define CVT_EN_LANG_ENGLISH_US'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_ENGLISH_US' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'ID_COUNTRY_INDIA' + '\n'
            ret += '#define CVT_DEF_LAUNCHER_SELECT'.ljust(_space) + 'ID_LAUNCHER_CVTE_LAUNCHER3_OVERSEA_SPACE' + '\n'
        elif self._android_system == self.android_4_4 and self._code_branch == 'fae':
            ret += '#define CVT_DEF_LANGUAGE_SELECT'.ljust(_space) + 'ID_LANGUAGE_CHINESE_CN' + '\n'
            ret += '#define CVT_EN_LANG_ENGLISH_US'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_EN_LANG_CHINESE_CN'.ljust(_space) + '1' + '\n'
            ret += '#define CVT_DEF_COUNTRY_SELECT'.ljust(_space) + 'ID_COUNTRY_CHINA' + '\n'
        else:
            pass

        ret += '//END\n'
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
