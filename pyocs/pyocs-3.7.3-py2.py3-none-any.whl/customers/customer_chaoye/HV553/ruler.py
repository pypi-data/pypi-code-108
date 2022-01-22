from customers.dtruler import DTRuler
from customers.customer_chaoye.parse_excel import ParseExcel
import json


class Ruler(DTRuler):
    # 客户ID
    _customer_id = 'CUSTOMER_CHAOYE'

    # 测试类型
    _test_type = 'F'

    # 订单需求
    _order_request_dir = None
    _order_number = None
    _country_code = None
    _logo_type = None
    _machine_type = None
    _board_type = None
    _panel_type = None
    _remote_type = None

    def __init__(self, ocs_demand, excel_para: str, excel_file_location: str):
        super(Ruler, self).__init__(ocs_demand=ocs_demand, excel_para=excel_para,\
                                    excel_file_location=excel_file_location)

        excel_obj = ParseExcel(self.excel_file_location)
        self._order_request_dir = excel_obj.get_order_request(self.line_number)
        self._order_number = self._order_request_dir['KEY1'][0]
        self._order_comment = self._order_request_dir['KEY1'][1]
        self._country_code = self._order_request_dir['KEY2'][0]
        self._logo_type = self._order_request_dir['KEY3'][0]
        self._machine_type = self._order_request_dir['KEY4'][0]
        self._board_type = self._order_request_dir['KEY5'][0]
        self._hardware_key = self._order_request_dir['KEY5'][1]
        self._panel_type = self._order_request_dir['KEY6'][0]
        self._language = self._order_request_dir['KEY8'][0]
        self._remote_type = self._order_request_dir['KEY9'][0]
        self._shipping_mode = self._order_request_dir['KEY10'][0]

    def get_ocs_modelid(self):
        """
        强制要求实现，获取model id
        :return: str : model id
        """
        if self._logo_type == '------':
            logo_type = 'NOLOGO'
        else:
            logo_type = "LOGO_" + self._logo_type

        model_id = 'CP' + str(self.ocs_demand.ocs_number) + '_CY_' + self._board_type + '_' + \
                   self.get_country_name() + '_' + self._panel_type + '_' + self._machine_type + '_' + \
                   self._remote_type + '_' + logo_type + '_' + self._order_number

        model_id = model_id.replace('.', '_').replace('-', '_').replace(' ', '_')

        return model_id

    def get_ocs_require(self):
        """
        强制要求实现，获取model id的配置内容
        :return:
        """
        model_id_head = '#elif ( IsModelID(' + self.get_ocs_modelid() + ') )' + '\n'
        hardware_macro = self.get_hardware_macro()
        sound_macro = self.get_sound_macro()
        panel_macro = self.get_panel_macro()
        logo_macro = self.get_logo_macro()
        remote_macro = self.get_remote_macro()
        language_macro = self.get_language_macro()
        country_macro = self.get_country_macro()
        app_macro = self.get_app_macro()
        other_macro = self.get_other_macro()
        software_config = model_id_head + hardware_macro + sound_macro + panel_macro + logo_macro + remote_macro + language_macro \
            + country_macro + app_macro + other_macro

        return software_config

    def get_code_branch(self):
        """
        强制要求实现，获取代码分支，用于提交配置
        :return: str : 代码分支

        """
        return self._code_branch

    def get_country_name(self):
        country_dict = self.get_config_res(self.country_config_resource)
        country_str = ""
        try:
            country_str = country_dict["default_country"][self._country_code]
            country_str = country_str.replace("ID_COUNTRY_", "")
        except KeyError:
            raise RuntimeError("警告： country_config.json文件中，还未配置添加" + self._country_code)

        return country_str

    def get_hardware_macro(self):
        hardware_macro = ''
        hardware_dict = self.get_config_res(self.hardware_config_resource)
        if self._hardware_key in list(hardware_dict):
            hardware_info = hardware_dict[self._hardware_key]
            board_type = hardware_info['board_type']
            dolby_type = hardware_info['dolby']
            current_ref = hardware_info['current_ref']
            hardware_macro = "//BOARD\n"
            hardware_macro += "#define CVT_DEF_BOARD_TYPE                              " + board_type + "\n"
            if dolby_type:
                hardware_macro += "#define CVT_EN_DOLBYPLUS                                    TRUE\n"
            if int(current_ref) != 0:
                hardware_macro += "#define CVT_DEF_CURRENT_REF_DUTY                        " + str(current_ref) + "\n"
            return hardware_macro
        else:
            raise RuntimeError("警告: hardware_config.json文件中，还未配置添加 " + self._hardware_key)
            return hardware_macro

    def get_charge_macro(self):
        charge_macro = ''
        charge_dict = self.get_config_res(self.hardware_config_resource)
        if self._hardware_key in list(charge_dict):
            charge_info = charge_dict[self._hardware_key]
            eshare_value = charge_info['eshare']
            gaia_value = charge_info['gaia']
            charge_macro = "//软件收费项\n"
            if int(eshare_value):
                charge_macro += "#define CVT_EN_APK_ESHARE                                   TRUE\n"
            if int(gaia_value):
                charge_macro += '#define CVT_DEF_LAUNCHER_TYPE                               ID_LAUNCHER_30_GAIA_20_NYS\n\
                                 #define CVT_DEF_LAUNCHER_30_SKIN                            ID_LAUNCHER_30_SKIN_NYS\n\
                                 #define CVT_EN_TV_STORE_PACKAGE                             "cm.aptoidetv.pt.cvt_hv553"'
            return charge_macro
        else:
            raise RuntimeError("警告: hardware_config.json文件中，还未配置添加 " + self._hardware_key)
            return charge_macro

    def get_sound_macro(self):
        machine_size = self._machine_type[0:3]
        sound_macro = "//AQ\n"
        if ("S" in self._machine_type) or ("L" in self._machine_type):
            if machine_size == "43D":
                sound_macro += "#define CVT_DEF_SOUND_TYPE                              ID_SOUND_AD82010_COMMON_CHAOYE_PC821_LOW_12V8R5W\n"
            if (machine_size == "50D") or (machine_size == "55D") or (machine_size == "65D"):
                sound_macro += "#define CVT_DEF_SOUND_TYPE                              ID_SOUND_AD82010_COMMON_CHAOYE_PC821_LOW_12V8R6W5\n"
            else:
                raise RuntimeError("警告: 未知的机型配置！")
        else:
            if machine_size == "75D":
                sound_macro += "#define CVT_DEF_SOUND_TYPE                              ID_SOUND_AD82010_COMMON_CHAOYE_81_75INCH_24V8R8W\n"
            elif (machine_size == "43D") or (machine_size == "50D") or (machine_size == "55D") or (machine_size == "65D"):
                sound_macro += "#define CVT_DEF_SOUND_TYPE                              ID_SOUND_AD82010_COMMON_CHAOYE_PC821_12V8R8W\n"
            else:
                raise RuntimeError("警告: 未知的机型配置！")
        return sound_macro

    def get_panel_macro(self):
        panel_macro = ''
        panel_dict = self.get_config_res(self.panel_config_resource)
        panel_name = self._panel_type
        panel_name = panel_name.strip()
        panel_name = panel_name.strip()
        panel_name = panel_name.replace(' ', '_')
        panel_name = panel_name.replace('-', '_')
        panel_name = panel_name.replace('.', '_')
        panel_name = panel_name.replace('(', '_')
        panel_name = panel_name.replace(')', '')
        if panel_name in list(panel_dict):
            panel_info = panel_dict[panel_name]
            panel_id = panel_info['panel_id']
            panel_macro = "//panel\n"
            panel_macro += "#define CVT_DEF_PANEL_TYPE                              " + str(panel_id) + "\n"
            return panel_macro
        else:
            raise RuntimeError("警告: panel_config.json文件中，还未配置添加 " + self._panel_type)
            return panel_macro

    def get_logo_macro(self):
        if (self._logo_type is None) or (self._logo_type == 'NOLOGO') or (self._logo_type == '------'):
            logo_macro = "//logo\n"
            logo_macro += "#define CVT_DEF_LOGO_TYPE                               ID_LOGO_CHAOYE_BLACK\n"
            return logo_macro
        else:
            logo_type = self._logo_type
            logo_type = logo_type.replace("-", "_")
            logo_type = logo_type.replace(" ", "_")
            logo_macro = "//logo\n"
            logo_macro += "#define CVT_DEF_LOGO_TYPE                               ID_LOGO_CHAOYE_" + logo_type + "\n"
            return logo_macro

    def get_remote_macro(self):
        remote_macro = ''
        remote_dict = self.get_config_res(self.ir_config_resource)
        if self._remote_type is None:
            return remote_macro
        else:
            remote_key = self._remote_type[0:9]
            try:
                remote_id = remote_dict[remote_key]
                remote_macro = "//ir & keypad\n"
                remote_macro += "#define CVT_DEF_IR_TYPE                                 " + remote_id + "\n"
            except KeyError:
                raise RuntimeError("警告: ir_config.json文件中，还未配置添加 " + remote_key)
            return remote_macro

    def get_language_macro(self):
        flag_default = '(默认)'
        language_dict = self.get_config_res(self.language_config_resource)
        language_list = self._language.split("、")
        language_default = ''
        language_option = []
        for i in range(0, len(language_list)):
            if flag_default in language_list[i]:
                language_default = language_list[i].replace(flag_default, "")
                language_option.append(language_default)
            else:
                language_option.append(language_list[i])
        language_default_dict = language_dict['Default_Language']
        language_option_dict = language_dict['Option_Language']
        language_macro = "//language\n"
        try:
            language_macro += language_default_dict[language_default] + "\n"
        except KeyError:
            raise RuntimeError("警告: language_config.json文件中，还未配置添加 " + language_default)
        for i in range(0, len(language_option)):
            try:
                language_macro += language_option_dict[language_option[i]] + "\n"
            except KeyError:
                raise RuntimeError("警告: language_config.json文件中，还未配置添加 " + language_option[i])

        return language_macro

    def get_country_macro(self):
        country_dict = self.get_config_res(self.country_config_resource)
        country_macro = "//country\n"
        try:
            default_country_codes = country_dict['default_country']
            default_country_id = default_country_codes[self._country_code]
            country_macro += "#define CVT_DEF_COUNTRY_SELECT                          " + default_country_id + "\n"
        except KeyError:
            raise RuntimeError("警告: country_config.json文件中，还未配置添加 " + self._country_code)
        return country_macro

    def get_app_macro(self):
        app_macro = "//Apk\n"
        order_comment = self._order_comment.upper()
        charge_dict = self.get_config_res(self.hardware_config_resource)
        if self._hardware_key in list(charge_dict):
            charge_info = charge_dict[self._hardware_key]
            eshare_value = charge_info['eshare']
        if "GOOGLE PLAY STORE" or "APP STORE" or "GOOGLEPLAY" in order_comment:
            app_macro += "#define CVT_EN_APP_GOOGLE_PLAY_STORE                    1\n"
        if "YOUTUBE" in order_comment:
            app_macro += "#define CVT_EN_APP_YOUTUBE                              1\n"
        if "NETFLIX" in order_comment:
            app_macro += "#define CVT_EN_APP_TV_NETFLIX                           1\n"
        if "FACEBOOK" in order_comment:
            app_macro += "#define CVT_EN_APP_ZEASN_FACEBOOK                       1\n"
        if "TWITTER" in order_comment:
            app_macro += "#define CVT_EN_APP_ZEASN_TWITTER                        1\n"
        if "SKYPE" in order_comment:
            app_macro += "#define CVT_EN_APP_CHAOYE_SKYPE                         1\n"
        if "AMAZON" in order_comment:
            app_macro += "#define CVT_EN_APP_ZEASN_AMAZON_PRIME                   1\n"
        if ("ESHARE" or "E-SHARE" in order_comment) and int(eshare_value):
            app_macro += "#define CVT_EN_APP_ESHARE                               1\n"
        return app_macro

    def get_other_macro(self):
        other_macro = "//Other\n"
        if "SENSY" in self._order_comment.upper:
            other_macro += "#define CVT_DEF_LAUNCHER_TYPE                         ID_LAUNCHER_SENSY_HYUNDAI\n"
        elif "VG" in self._order_comment.upper:
            other_macro += "#define CVT_DEF_LAUNCHER_TYPE                         ID_LAUNCHER_SENSY_VG\n"
        if self._shipping_mode == '整机':
            other_macro += "#define CVT_DEF_CHANNEL_TABLE                 ID_CHANNEL_TABLE_CHAOYE\n\
                            #define CVT_EN_UP_FW_HAVE_CHANNEL_TABLE       1\n\
                            #define CVT_EN_F1_RESET_IMPORTCUSCH           1"
        other_macro += "//END\n"
        return other_macro
