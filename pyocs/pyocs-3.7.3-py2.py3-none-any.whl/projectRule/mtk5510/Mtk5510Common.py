import abc
from pyocs.pyocs_interface import UniteInterface
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *
from customers.customer_common.common_database import commonDataBase

class Mtk5510Common(UniteInterface):

    atv_chip = ('MT5510DHMT', 'MT5510DHNT', 'MT5510AHNT')

    def get_board_macro(self):
        # 主板宏：CVT_DEF_BOARD_TYPE  ID_BD_[主方案:MTK5510]_[板型:81]_SUB_CH_[子板型:A1]
        product_split_list = self.request_dict[self.ocs_demand.product_name].split('.')
        board_type = product_split_list[2]
        # 5510 部分特殊的版型需要作区分
        if board_type == 'PB752' or board_type == 'PB805':
            main_project = 'MT5510I'
        elif board_type == 'PB757':
            main_project = 'MT5510S'
        else:
            main_project = product_split_list[1].rstrip('S').rstrip('T').rstrip('I')
        sub_board_split_list = self.request_dict[self.ocs_demand.port_name].split('_')
        sub_board_type = sub_board_split_list[1]
        board_macro = "ID_BD_" + main_project + "_" + board_type + "_SUB_CH_" + sub_board_type
        ret = "#define CVT_DEF_BOARD_TYPE".ljust(self._space) + board_macro + '\n'
        return ret

    def get_chip_macro(self):
        # 主芯片宏：CVT_DEF_CHIP_TYPE ID_CHIP_[芯片名：MT5510ZHOJ]
        chip_remark = self.request_dict[self.ocs_demand.chip_remark]
        chip_type_list = self.request_dict[self.ocs_demand.chip_name].split('(')
        chip_type = chip_type_list[0]
        chip_macro = "ID_CHIP_" + chip_type
        ret = "#define CVT_DEF_CHIP_TYPE".ljust(self._space) + chip_macro + '\n'
        if chip_type in self.atv_chip:
            ret += "#define CVT_EN_SOURCE_DTV".ljust(self._space) + '0' + '\n'
        if self._code_branch == 'fae_eu' and (not "DVB" in chip_remark) \
                and ("ISDB" in chip_remark or "ATSC" in chip_remark):
            ret += "#define CVT_EN_SOURCE_DTV".ljust(self._space) + '0' + '\n'
        if self._code_branch == 'fae_sa' and (not "ISDB" in chip_remark) \
                and ("DVB" in chip_remark or "ATSC" in chip_remark):
            ret += "#define CVT_EN_SOURCE_DTV".ljust(self._space) + '0' + '\n'
        if self._code_branch == 'fae_us' and (not "ATSC" in chip_remark) \
                and ("DVB" in chip_remark or "ISDB" in chip_remark):
            ret += "#define CVT_EN_SOURCE_DTV".ljust(self._space) + '0' + '\n'
        return ret

    def get_flash_size_macro(self):
        # Flash Size宏：ID_FLASH_SIZE_[Flash Size：8G]
        flash_size = self.request_dict[self.ocs_demand.flash_size_name].strip('Byte')
        flash_size_macro = "ID_FLASH_SIZE_" + flash_size
        ret = "#define CVT_DEF_FLASH_SIZE".ljust(self._space) + flash_size_macro + '\n'
        return ret

    def get_pwm_macro(self):
        # Pwm占空比宏：[占空比：60]
        pwm_macro = self.request_dict[self.ocs_demand.pwm_name]
        ret = "#define CVT_DEF_PWM_REF_MAX".ljust(self._space) + pwm_macro + '\n'
        return ret

    def get_wifi_macro(self):
        # WIFI TYPE
        ret = ''
        wifi_type_str = ''
        if not self.request_dict[self.ocs_demand.wifi_bluetooth_type]:
            if self.request_dict[self.ocs_demand.wifi_module_info]:
                wifi_type_str = self.request_dict[self.ocs_demand.wifi_module_info]
        else:
            wifi_type_str = self.request_dict[self.ocs_demand.wifi_bluetooth_type]

        if 'M06USA1' in wifi_type_str:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_MT7601U' + '\n'
        elif 'MT7603U' in wifi_type_str:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_MT7603U' + '\n'
        elif 'RTK8192' in wifi_type_str:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_RTK8192' + '\n'
        elif 'SKI.W6022.1' in wifi_type_str:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_ATBM6022' + '\n'
        elif 'M632USA1' in wifi_type_str:
            ret += '#define CVT_DEF_WIFI_TYPE'.ljust(self._space) + 'ID_WIFI_TYPE_MT7662U' + '\n'
        return ret

    def get_ci_macro(self):
        # CI PLUS
        ret = ''
        if (not self.request_dict[self.ocs_demand.ci_type]) and self.request_dict[self.ocs_demand.ciplus_name] == '无':
            pass
        elif 'CI_Plus' in self.request_dict[self.ocs_demand.ciplus_name]:
            ret += '#define CVT_DEF_CI_TYPE'.ljust(self._space) + 'ID_CI_TYPE_CI_PLUS' + '\n'
        elif "CI" in self.request_dict[self.ocs_demand.ci_type]:
            ret += '#define CVT_DEF_CI_TYPE'.ljust(self._space) + 'ID_CI_TYPE_CI' + '\n'
        return ret

    def get_eshare_macro(self):
        # ESHARE
        ret = ''
        other_app_list = self.request_dict[self.ocs_demand.other_app_soft]
        if other_app_list and 'Eshare' in other_app_list:
            ret += '#define CVT_EN_APP_ESHARE'.ljust(self._space) + '1' + '\n'
        return ret

    def get_ddr_macro(self):
        ret = ''
        ddr_str = self.ocs_demand.get_ddr_size()
        if "512M" in ddr_str:
            ret = '#define CVT_DEF_DDR_SIZE'.ljust(self._space) + 'ID_DDR_512M' + '\n'
        elif "1G" in ddr_str:
            ret = '#define CVT_DEF_DDR_SIZE'.ljust(self._space) + 'ID_DDR_1G' + '\n'
        return ret

    def get_code_branch(self):
        region_name_list = self.request_dict[self.ocs_demand.region_name]
        if not region_name_list:
            raise NoRegionError('此单无区域')
        map_list = commonDataBase().get_region_mapping_info_by_country(region_name_list)
        tv_system_str = map_list[0]
        country_region_str = map_list[1]
        if not tv_system_str:
            raise OcsRegionError('无法查询到此区域的制式')
        if self.ocs_demand.get_chip_name().split('(')[0] in self.atv_chip:
            self._code_branch = 'fae_eu'  # 如果芯片为纯模拟的芯片，则全部在fae_eu出
        elif 'ATV' in tv_system_str:
            if country_region_str == '欧洲':
                self._code_branch = 'fae_eu'
            elif country_region_str == '南美':
                self._code_branch = 'fae_sa'
            elif country_region_str == '北美':
                self._code_branch = 'fae_us'
            else:
                raise RuntimeError('该国家不属于区域支持所属范围，请确认，谢谢！')
        elif 'DVB' in tv_system_str:
            self._code_branch = 'fae_eu'
        elif 'ISDB' in tv_system_str:
            self._code_branch = 'fae_sa'
        elif 'ATSC' in tv_system_str:
            self._code_branch = 'fae_us'
        else:
            raise RuntimeError('该方案不支持此制式，或者检查该国家制式是否正确，谢谢！')
        return self._code_branch

    def get_tuner_macro(self):
        ret = ''
        tuner_type_str = self.request_dict[self.ocs_demand.tuner_name]
        if '11980FNPRD' in tuner_type_str:
            ret += '#define CVT_DEF_SECOND_TUNER_TYPE'.ljust(self._space) + 'ID_TUNER_TYPE_RAFAEL_RT710_EDS_11980FNPRD' + '\n'
        return ret


    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass