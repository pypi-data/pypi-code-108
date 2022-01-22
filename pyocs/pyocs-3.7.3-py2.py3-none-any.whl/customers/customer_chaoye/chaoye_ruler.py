from customers.dtruler import DTRuler
import abc
from customers.customer_chaoye.parse_excel import ParseExcel


class ChaoYeRuler(DTRuler):

    # excel数据，订单需求
    _order_request_dir = None
    _order_number = None
    _order_comment = None
    _country_code = None
    _logo_type = None
    _machine_type = None
    _board_type = None
    _hardware_key = None
    _panel_type = None
    _language = None
    _remote_type = None
    _shipping_mode = None
    language_default = None
    ir_mark_num = 9  # 默认识别excel中遥控器的九位，可以根据不同方案需求重写

    # json数据，配置资源
    country_dict = None
    panel_dict = None

    def __init__(self, ocs_demand, excel_para: str, excel_file_location: str):
        """
        从excel表格中获取数据
        :param ocs_demand:
        :param excel_para:
        :param excel_file_location:
        """
        super(ChaoYeRuler, self).__init__(ocs_demand=ocs_demand, excel_para=excel_para,
                                          excel_file_location=excel_file_location)

        excel_obj = ParseExcel(self.excel_file_location)
        self._order_request_dir = excel_obj.get_order_request(self.line_number)
        self._order_number = self._order_request_dir['KEY1'][0]   # 订单号
        try:
            self._order_comment = self._order_request_dir['KEY1'][1]   # 摘要公共需求
        except:
            pass
        self._country_code = self._order_request_dir['KEY2'][0]   # 国家
        self._logo_type = self._order_request_dir['KEY3'][0]   # logo
        self._machine_type = self._order_request_dir['KEY4'][0]   # 机型
        self._board_type = self._order_request_dir['KEY5'][0]   # 板型
        self._hardware_key = self._order_request_dir['KEY5'][1]   # 料号
        self._panel_type = self._order_request_dir['KEY6'][0]   # 屏
        self._language = self._order_request_dir['KEY8'][0]   # 语言
        self._remote_type = self._order_request_dir['KEY9'][0]   # 遥控器
        self._shipping_mode = self._order_request_dir['KEY10'][0]  # 出货方式

        self.country_dict = self.get_config_res('country')
        self.panel_dict = self.get_config_res(self.panel_config_resource)

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

    @abc.abstractmethod
    def get_code_branch(self):
        pass

    def resource_check(self):
        check_result = dict()
        check_result[self.hardware_config_resource] = True if self.hardware_resource_check() else \
            ("警告: hardware_config.json文件中，还未配置添加 " + self._hardware_key)
        if self.panel_dict:
            check_result[self.panel_config_resource] = True if self.panel_resource_check() else \
                ("警告: panel_config.json文件中，还未配置添加 " + self._panel_type)
        mark, data, message = self.ir_resource_check()
        check_result[self.ir_config_resource] = True if mark else \
            ("警告: ir_config.json文件中，还未配置添加 " + message)
        language_list, default_language, is_ng = self.language_resource_check()
        check_result["default_language"] = True if default_language else \
            ("警告: language_config.json文件中，还未配置添加默认语言：" + self.language_default)
        check_result["language_option"] = True if not is_ng else \
            ("警告: language_config.json文件中，还未配置添加可选语言：" + language_list)
        if self.country_dict:
            check_result["default_country"] = True if self.country_resource_check() else \
                ("警告： country_config.json文件中，还未配置添加" + self._country_code)
        return check_result

    def hardware_resource_check(self):
        hardware_dict = self.get_config_res(self.hardware_config_resource)
        if self._hardware_key in list(hardware_dict):
            return hardware_dict[self._hardware_key]
        else:
            return None

    def panel_resource_check(self):
        panel_name = self._panel_type
        panel_name = panel_name.strip()
        panel_name = panel_name.replace(' ', '_')
        panel_name = panel_name.replace('-', '_')
        panel_name = panel_name.replace('.', '_')
        panel_name = panel_name.replace('(', '_')
        panel_name = panel_name.replace(')', '')
        if panel_name in list(self.panel_dict):
            return self.panel_dict[panel_name]
        else:
            return None

    def ir_resource_check(self):
        mark = True
        message = ""
        data = None
        remote_dict = self.get_config_res(self.ir_config_resource)
        if not self._remote_type:
            message = "需求表中没有发现遥控器"
            mark = False
            return mark, data, message
        remote_key = self._remote_type[0:self.ir_mark_num]
        if remote_key in list(remote_dict):
            data = remote_dict[remote_key]
        else:
            mark = False
            message = remote_key + "在json表中没有发现映射关系"
        return mark, data, message

    def language_resource_check(self):
        flag_default = '(默认)'
        language_dict = self.get_config_res(self.language_config_resource)
        language_list = self._language.split("、")

        language_option = []
        ok_language = []
        ng_language = []
        is_ng = False
        for i in range(0, len(language_list)):
            if flag_default in language_list[i]:
                self.language_default = language_list[i].replace(flag_default, "")
                language_option.append(self.language_default)
            else:
                language_option.append(language_list[i])
        language_default_dict = language_dict['Default_Language']
        language_option_dict = language_dict['Option_Language']

        if self.language_default in list(language_default_dict):
            default_language = language_default_dict[self.language_default]
        else:
            default_language = None
        for language in language_option:
            if language in list(language_option_dict):
                ok_language.append(language_option_dict[language])
            else:
                ng_language.append(language)
                is_ng = True
        language_option_list = ng_language if ng_language else ok_language
        return default_language, language_option_list, is_ng

    def country_resource_check(self):
        cus_country_dict = self.country_dict["default_country"]
        if self._country_code in list(cus_country_dict):
            return cus_country_dict[self._country_code]
        else:
            return None
