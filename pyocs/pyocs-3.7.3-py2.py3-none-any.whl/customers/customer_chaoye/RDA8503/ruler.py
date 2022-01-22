from customers.customer_chaoye.chaoye_ruler import ChaoYeRuler


class Ruler(ChaoYeRuler):
    # 客户ID
    _customer_id = 'CUSTOMER_CHAOYE'

    # 测试类型
    _test_type = 'F'

    board_macro_name = "CVT_DEF_BOARD_TYPE"
    chip_macro_name = "CVT_DEF_CHIPSET"
    pwm_macro_name = "CVT_DEF_CURRENT_REF_DUTY"
    aq_macro_name = "CVT_DEF_SOUND_TYPE"
    panel_macro_name = "CVT_DEF_PANEL_TYPE"
    logo_macro_name = "CVT_DEF_LOGO_TYPE"
    ir_macro_name = "CVT_DEF_IR_TYPE"
    default_language_macro_name = "CVT_DEF_LANGUAGE_SELECT"

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
                   self._panel_type + '_' + self._machine_type + '_' + \
                   self._remote_type + '_' + logo_type + '_' + self._order_number

        model_id = model_id.replace('.', '_').replace('-', '_').replace(' ', '_')

        return model_id

    def get_ocs_require(self):
        """
        强制要求实现，获取model id的配置内容
        :return:
        """
        model_id_head = '#elif(IsModelID(' + self.get_ocs_modelid() + '))' + '\n'
        hardware_macro = self.get_hardware_macro()
        sound_macro = self.get_sound_macro()
        panel_macro = self.get_panel_macro()
        logo_macro = self.get_logo_macro()
        remote_macro = self.get_remote_macro()
        language_macro = self.get_language_macro()
        other_macro = self.get_other_macro()

        software_config = model_id_head + hardware_macro + sound_macro + panel_macro + logo_macro + \
                          remote_macro + language_macro + other_macro

        return software_config

    def get_code_branch(self):
        """
        强制要求实现，获取代码分支，用于提交配置
        :return: str : 代码分支
        """
        return "chaoye"

    def get_hardware_macro(self):
        hardware_info = self.hardware_resource_check()
        board_type = hardware_info['board_type']
        chip_type = hardware_info['chip_type']
        current_ref = hardware_info['current_ref']
        hardware_macro = "//board\n"
        hardware_macro += self.get_macro_line(self.board_macro_name, board_type)
        if chip_type == "RDA8503_D":
            hardware_macro += self.get_macro_line(self.chip_macro_name, chip_type)
        hardware_macro += self.get_macro_line(self.pwm_macro_name, str(current_ref))
        return hardware_macro

    def get_sound_macro(self):
        machine_size = self._machine_type[0:3]
        sound_macro = "//sound\n"
        machine_name = self._machine_type.upper()

        if "S" in machine_name or "L" in machine_name:
            if machine_size == "24":
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_CS8563S_CHAOYE_MUSIC_20DB5V4R3W")
            elif machine_size == "28D" or machine_size == "32D":
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CY_MUISC_V7_ASIA_PB816_20DB12V8R5W")
            elif machine_size == "39D" or machine_size == "40D" or machine_size == "43D":
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CY_MUISC_V7_ASIA_PB801_20DB12V8R5W")
            elif machine_size == "49D" or machine_size == "50D":
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CY_MUISC_V8_ASIA_PB801_20DB12V8R6W")
            else:
                raise RuntimeError("警告:未知的机型, CVT_DEF_SOUND_TYPE 未有对应值!!")
        else:
            if (machine_size == "20D") or (machine_size == "22D") or (machine_size == "24D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_CS8563S_CHAOYE_ASIA_20DB5V4R3W")
            elif (machine_size == "28D") or (machine_size == "32D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CHAOYE_V7_PB816_20DB12V8R8W")
            elif (machine_size == "39D") or (machine_size == "40D") or (machine_size == "43D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CHAOYE_V7_ASIA_PB801_20DB12V8R8W")
            elif (machine_size == "49D") or (machine_size == "50D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CHAOYE_V8_ASIA_PB801_20DB12V8R8W")
            else:
                raise RuntimeError("警告:未知的机型, CVT_DEF_SOUND_TYPE 未有对应值!!")

        return sound_macro

    def get_panel_macro(self):
        panel_info = self.panel_resource_check()
        panel_id = panel_info['panel_id']
        panel_lvds_map = panel_info['lvds_map']
        panel_mirror = panel_info['mirror']

        panel_macro = "//panel\n"
        panel_macro += self.get_macro_line(self.panel_macro_name, str(panel_id))
        if panel_lvds_map != 0:
            panel_macro += self.get_macro_line("CVT_DEF_PANEL_LVDS_MAP_4_CPS", str(panel_lvds_map))
        if panel_mirror:
            panel_macro += self.get_macro_line("CVT_DEF_PANEL_MIRROR_TYPE","PL_MIRROR_BOTH_HV")

        return panel_macro

    def get_logo_macro(self):
        logo_macro = ''
        if (self._logo_type is None) or (self._logo_type == 'NOLOGO') or (self._logo_type == '------'):
            return logo_macro
        else:
            logo_type = self._logo_type
            logo_type = logo_type.replace("-", "_")
            logo_type = logo_type.replace(" ", "_")
            logo_macro = "//logo\n"
            logo_macro += self.get_macro_line(self.logo_macro_name, "ID_LOGO_CHAOYE_" + logo_type)
            return logo_macro

    def get_remote_macro(self):
        mark, data, message = self.ir_resource_check()
        remote_id = data
        remote_macro = "//ir\n"
        remote_macro += self.get_macro_line(self.ir_macro_name, remote_id)
        return remote_macro

    def get_language_macro(self):
        language_macro = "//language\n"
        
        default_language, language_option, is_ng = self.language_resource_check()
        language_macro += self.get_macro_line(self.default_language_macro_name, default_language)

        for language in language_option:
            language_macro += self.get_macro_line(language, "1")

        return language_macro

    def get_other_macro(self):
        other_macro = "//other\n"
        if "图文" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_SUPPORT_TTX", "1")
        if self._shipping_mode == '整机':
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_FAC_RESET","1")
        else:
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_FAC_SKD_MODE", "1")

        if "OSD复位抓图LOGO" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_DISPLAY_DEFAULT_LOGO_WHEN_MENU_RESET", "1")

        if "USB1 拷贝到 USB2 的功能" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_SUPPORT_MEDIA_COPY_FILE", "1")

        other_macro += "//END\n"
        return other_macro
