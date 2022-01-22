from customers.customer_chaoye.chaoye_ruler import ChaoYeRuler


class Ruler(ChaoYeRuler):
    # 客户ID
    _customer_id = 'CUSTOMER_CHAOYE'

    # 测试类型
    _test_type = 'F'

    board_macro_name = "CVT_DEF_BOARD_TYPE"
    chip_macro_name = "CVT_DEF_CHIP_TYPE"
    flash_macro_name = "CVT_DEF_FLASH_SIZE"
    pwm_macro_name = "CVT_DEF_CURRENT_REF_DUTY"
    aq_macro_name = "CVT_DEF_SOUND_TYPE"
    panel_macro_name = "CVT_DEF_PANEL_TYPE"
    panel_mirror_macro_name = "CVT_EN_MIRROR"
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

    def get_android_system(self):
        """
        非强制实现，获取安卓系统版本，仅用于358等类似的一个方案出两种系统的逆天方案
        :return: str : 安卓版本
        """
        self._android_system = self.android_4_4
        if '1G' in self._order_comment and '8G' in self._order_comment:
            self._android_system = self.android_8_0
        else:
            self._android_system = self.android_4_4

        return self._android_system

    def get_code_branch(self):
        """
        强制要求实现，获取代码分支，用于提交配置
        :return: str : 代码分支

        """
        if '1G' in self._order_comment and '8G' in self._order_comment:
            return 'fae'
        else:
            return 'oversea'

    def get_country_name(self):
        country_str = self.country_resource_check().replace("ID_COUNTRY_", "")
        return country_str

    def get_hardware_macro(self):
        hardware_info = self.hardware_resource_check()
        board_type = hardware_info['board_type']
        chip_type = hardware_info['chip_type']
        flash_size = hardware_info['flash_size']
        current_ref = hardware_info['current_ref']
        hardware_macro = "//--------------------------------- Board ----------------------------------\n"
        hardware_macro += self.get_macro_line(self.board_macro_name, board_type)
        hardware_macro += self.get_macro_line(self.chip_macro_name, chip_type)
        hardware_macro += self.get_macro_line(self.flash_macro_name, flash_size)
        hardware_macro += self.get_macro_line(self.pwm_macro_name , str(current_ref))
        return hardware_macro


    def get_sound_macro(self):
        machine_size = self._machine_type[0:3]
        sound_macro = "//--------------------------------- Sound ---------------------------------\n"
        if ("S" in self._machine_type) or ("L" in self._machine_type):
            if (machine_size == "32D") or (machine_size == "43D") or (machine_size == "39D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CHAOYE_MUSIC_PB801_12V8R5W")
            elif (machine_size == "49D") or (machine_size == "50D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CHAOYE_MUSIC_PB801_12V8R6W")
            else:
                raise RuntimeError("警告: 未知的机型配置！")
        else:
            if (machine_size == "32D") or (machine_size == "43D") or (machine_size == "39D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,
                                                   "ID_SOUND_RDA3118_CHAOYE_PB801_12V8R7W")
            elif (machine_size == "49D") or (machine_size == "50D"):
                sound_macro += self.get_macro_line(self.aq_macro_name,"ID_SOUND_RDA3118_CHAOYE_PB801_12V8R8W")
            else:
                raise RuntimeError("警告: 未知的机型配置！")

        return sound_macro

    def get_panel_macro(self):
        panel_info = self.panel_resource_check()
        panel_id = panel_info['panel_id']
        panel_lvds_map = panel_info['lvds_map']
        panel_mirror = panel_info['mirror']
        panel_free_run = panel_info['free_run']

        panel_macro = "//-------------------------------- Panel ----------------------------------\n"
        panel_macro += self.get_macro_line(self.panel_macro_name, str(panel_id))
        if panel_lvds_map != 0:
            panel_macro += self.get_macro_line("CVT_DEF_PANEL_LVDS_MAP", str(panel_lvds_map))
        if panel_mirror:
            panel_macro += self.get_macro_line(self.panel_mirror_macro_name, "1")
        if panel_free_run:
            panel_macro += self.get_macro_line("CVT_EN_PNL_FREERUN", "1")

        return panel_macro

    def get_logo_macro(self):
        logo_macro = ''
        if (self._logo_type is None) or (self._logo_type == 'NOLOGO') or (self._logo_type == '------'):
            return logo_macro
        else:
            logo_type = self._logo_type
            logo_type = logo_type.replace("-", "_")
            logo_type = logo_type.replace(" ", "_")
            logo_macro = "//--------------------------------- LOGO ------------------------------------\n"
            logo_macro += self.get_macro_line(self.logo_macro_name, "ID_LOGO_CHAOYE_" + logo_type)
            return logo_macro

    def get_remote_macro(self):
        mark, data, message = self.ir_resource_check()
        remote_id = data
        remote_macro = "//--------------------------------- IR ------------------------------------\n"
        remote_macro += self.get_macro_line(self.ir_macro_name, remote_id)
        return remote_macro

    def get_language_macro(self):
        language_macro = "//------------------------------- Language --------------------------------\n"
        default_language, language_option, is_ng = self.language_resource_check()
        language_macro += self.get_macro_line(self.default_language_macro_name, default_language)

        for language in language_option:
            language_macro += self.get_macro_line(language, "1")

        return language_macro

    def get_country_macro(self):
        country_macro = "//------------------------------- Country --------------------------------\n"

        default_country_id = self.country_resource_check()
        country_macro += self.get_macro_line(self.default_language_macro_name, default_country_id)

        return country_macro

    def get_app_macro(self):
        app_macro = "//------------------------------- App -----------------------------------\n"
        order_comment = self._order_comment.upper()
        if ("GOOGLE PLAY STORE" in order_comment) or ("APP STORE" in order_comment) or\
           ("GOOGLEPLAY" in order_comment):
            app_macro += self.get_macro_line("CVT_EN_APP_GOOGLE_PLAY_STORE", "1")
        if "YOUTUBE" in order_comment:
            app_macro += self.get_macro_line("CVT_EN_APP_YOUTUBE_TV_VIDEO", "1")
        if "NETFLIX" in order_comment:
            app_macro += self.get_macro_line("CVT_EN_APP_NETFLIX", "1")
        if "FACEBOOK" in order_comment:
            app_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_FACEBOOK", "1")
        if "TWITTER" in order_comment:
            if self.get_android_system() == '4_4':
                app_macro += self.get_macro_line("CVT_EN_PREINSTALL_APK", "1")
                app_macro += self.get_macro_line("CVT_DEF_STR_APKS_FOLDER", "chaoye_twitter")
            else:
                app_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_TWITTER", "1")
        if "SKYPE" in order_comment:
            app_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_SKYPE", "1")
        if ("MIRACAST" in order_comment) or ("手机同屏" in order_comment):
            app_macro += self.get_macro_line("CVT_EN_APP_MIRACAST", "1")
        if ("ESHARE" in order_comment) or ("E-SHARE" in order_comment):
            app_macro += self.get_macro_line("CVT_EN_APP_ESHARE", "1")

        return app_macro

    def get_other_macro(self):
        other_macro = "//------------------------------ Other ----------------------------------\n"
        if "图文" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_TTX", "1")
        if self._shipping_mode == '整机':
            other_macro += self.get_macro_line("CVT_DEF_CUS_FAC_CHANNEL_TABLE", "ID_CHANNEL_TABLE_CHAOYE")

        other_macro += "//END\n"
        return other_macro
