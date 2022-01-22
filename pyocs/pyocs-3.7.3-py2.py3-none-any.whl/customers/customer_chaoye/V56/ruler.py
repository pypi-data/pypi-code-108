import re
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
    panel_mirror_macro_name = "CVT_EN_MIRROR"
    logo_macro_name = "CVT_DEF_LOGO_TYPE"
    ir_macro_name = "CVT_DEF_IR_TYPE"
    default_language_macro_name = "CVT_DEF_LANGUAGE_SELECT"
    keypad_macro_name = "CVT_DEF_KEYPAD_TYPE"

    ir_mark_num = 7

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
        keypad_macro = self.get_keypad_macro()

        software_config = model_id_head + hardware_macro + sound_macro + panel_macro + logo_macro + keypad_macro + \
                          remote_macro + language_macro + other_macro

        return software_config

    def get_code_branch(self):
        """
        强制要求实现，获取代码分支，用于提交配置
        :return: str : 代码分支
        """
        return "chaoye"

    def get_hardware_macro(self):
        """
        根据料号将硬件信息从json中抓取并配置相应宏
        :return:
        """
        hardware_info = self.hardware_resource_check()
        board_type = hardware_info['board_type']
        chip_type = hardware_info['chip_type']
        current_ref = hardware_info['current_ref']
        hardware_macro = "//board\n"
        hardware_macro += self.get_macro_line(self.board_macro_name, board_type)
        hardware_macro += self.get_macro_line(self.chip_macro_name, chip_type)
        hardware_macro += self.get_macro_line(self.pwm_macro_name, str(current_ref))
        return hardware_macro

    def get_sound_macro(self):
        """
        sound
        :return:
        """
        board_name = self._board_type
        machine_size = re.sub("\D", "", self._machine_type)[:-1]
        sound_macro = "//sound\n"

        machine_name = self._machine_type.upper()
        hornflag = machine_name.find('S')!=-1 or machine_name.find('L')!=-1
        # hornflag < 0 #普通喇叭
        # horflag  > 0 #音响喇叭

        if str(board_name) == "TP.V56.PA671":
            sound_macro += self.switch_v56_PA671_sound(machine_size, int(hornflag))
        elif str(board_name) == "TP.V56.PB801":
            sound_macro += self.switch_v56_PB801_sound(machine_size, int(hornflag))
        elif str(board_name) == "TP.V56.PB826":
            sound_macro += self.switch_v56_PB826_sound(machine_size, int(hornflag))
        elif str(board_name) == "TP.V56.PB816":
            sound_macro += self.switch_v56_PB816_sound(machine_size, int(hornflag))
        elif str(board_name) == "TP.V56.PB842":
            sound_macro += self.switch_v56_PB842_sound(machine_size, int(hornflag))
        else:
            raise RuntimeError("警告:未知的机型, CVT_DEF_SOUND_TYPE 未有对应值!!")
        return sound_macro

    def switch_v56_PA671_sound(self, sizenum, hornflag):
        if hornflag <= 0:
            if int(sizenum) <= 24:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_YD1517_CHAOYE_V56_PA671_MODELNAME_26DB12V4R3W")
            else:
                soundstr = "SOUND_ERROR"
        else:
            if int(sizenum) <= 24:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_YD1517_CHAOYE_TEST_LOW_V56_PA671_MODELNAME_26DB12V4R3W")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FO", "180")
                soundstr += self.get_macro_line("CVT_DEF_HPF_QVALUE", "40")
            else:
                soundstr = "SOUND_ERROR"
        return soundstr

    def switch_v56_PB801_sound(self, sizenum, hornflag):
        if hornflag <= 0:  # 普通喇叭
            if int(sizenum) >= 30 and int(sizenum) <= 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_CSY1281_CHAOYE_V56_PB801A_MODELNAME_26DB12V8R7W")
            elif int(sizenum) > 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_CSY1281_CHAOYE_V56_PB801A_MODELNAME_26DB12V8R8W")
            else:
                soundstr = "SOUND_ERROR"
        else:
            if int(sizenum) >= 30 and int(sizenum) <= 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_CSY1281_CHAOYE_TEST_LOW_FRQ_V56_PB801A_MODELNAME_26DB12V8R5W")
            elif int(sizenum) > 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                           "ID_SOUND_CSY1281_CHAOYE_TEST_LOW_FRQ_V56_PB801A_MODELNAME_26DB12V8R65W")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FO", "200")
                soundstr += self.get_macro_line("CVT_DEF_HPF_QVALUE", "40")
            else:
                soundstr = "SOUND_ERROR"
        return soundstr

    def switch_v56_PB826_sound(self, sizenum, hornflag):
        if hornflag <= 0:  # 普通喇叭
            if int(sizenum) >= 30 and int(sizenum) <= 40:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_CSY1281_CHAOYE_V56_PB826_MODELNAME_26DB12V8R7W")
            else:
                soundstr = "SOUND_ERROR"
        else:
            if int(sizenum) >= 30 and int(sizenum) <= 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_CSY1281_CHAOYE_TEST_LOW_FRQ_V56_PB826_MODELNAME_26DB12V8R5W")
            else:
                soundstr = "SOUND_ERROR"
        return soundstr

    def switch_v56_PB816_sound(self, sizenum, hornflag):
        if hornflag <= 0:  # 普通喇叭
            if int(sizenum) >= 30 and int(sizenum) <= 40:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_CSY1281_CHAOYE_V56_PB801A_MODELNAME_26DB12V8R7W")
            else:
                soundstr = "SOUND_ERROR"
        else:
            soundstr = "SOUND_ERROR"
        return soundstr

    def switch_v56_PB842_sound(self, sizenum, hornflag):
        if hornflag <= 0:  # 普通喇叭
            if int(sizenum) <= 24:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_OB6220_CHAOYE_V56_PB842_26DB12V8R3W")
            elif int(sizenum) >= 32 and int(sizenum) <= 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_OB6220_CHAOYE_V56_PB842_26DB12V8R7W")
            else:
                soundstr = "SOUND_ERROR"
        else:
            if int(sizenum) <= 24:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_OB6220_CHAOYE_MUSIC_V56_PB842_26DB12V8R3W")
            elif int(sizenum) >= 32 and int(sizenum) <= 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_OB6220_CHAOYE_MUSIC_V56_PB842_26DB12V8R5W")
            else:
                soundstr = "SOUND_ERROR"
        return soundstr

    def get_panel_macro(self):
        """
        panel
        :return:
        """
        panel_dict = self.get_config_res(self.panel_config_resource)

        panel_name = self._panel_type
        panel_name = panel_name.strip()
        panel_name = panel_name.replace(' ', '-')
        panel_name = panel_name.replace('(', '-')
        panel_name = panel_name.replace(')', '')

        panel_macro = "//panel\n"
        panel_macro += self.createpanel(panel_name)
        return panel_macro

    def createpanel(self, panel):
        panelstr = ''
        if panel == 'PT320AT01-1' or \
                panel == 'HV320WHB-N5N' or \
                panel == 'HV320WHB-N5M' or \
                panel == 'ST2751A01-8':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_HV320WHB_N00")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '1')

        elif panel == 'HV236WHB-N41'or \
                panel == 'V236BJ1-P01':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1366_768")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '1')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '1')

        elif panel == 'HV236WHB-N00':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1366_768")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '1')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '0')

        elif panel == 'LC390TA2A'or \
                panel == 'LC390TU2A' or \
                panel == 'LC390TU1A':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_T390XVNO1_0")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '1')
        elif panel == 'T390XVN02.0':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_T390XVNO1_0")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '3')
        elif panel == 'HV320WHB-N00' or \
             panel == 'HV320WHB-N80' or \
             panel == 'LSC320AN09' or \
             panel == 'HV320WX2-206' or \
             panel == 'LSC320AN10':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_HV320WHB_N00")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '1')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '0')

        elif panel == 'HV320WHB-N85' or \
             panel == 'HV320WHB-N5B' or \
             panel == 'HV320WHB-N8B':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_HV320WHB_N00")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '3')

        elif panel == 'HV320WHB-N86':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_HV320WHB_N86_TCON")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '0')

        elif panel == 'HV320WHB-N55' or \
             panel == 'HV320WHB-N56' or \
             panel == 'T320XVN02.G' or \
             panel == 'V320BJ6-Q01':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_HV320WHB_N00")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '0')

        elif panel == 'V320BJ8-Q01':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1366_768")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '3')
                panelstr += self.get_macro_line('CVT_EN_FORCE_FREE_RUN', 'TRUE')

        elif panel == 'HV430FHB-N10' or \
             panel == 'T430HVN01.0' or \
             panel == 'HV430FHB-N40':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_HV430FHB_N40")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '0')
                panelstr += self.get_macro_line('CVT_EN_FORCE_FREE_RUN', '1')
                panelstr += self.get_macro_line('CVT_DEF_SSC_LVDS_VALUE', '0')

        elif panel == 'HV490FHB-N8F' or \
             panel == 'HV490FHB-N8G':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1920_1080")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '1')
                panelstr += self.get_macro_line('CVT_DEF_SSC_LVDS_VALUE', '0')
                panelstr += self.get_macro_line('CVT_EN_FORCE_FREE_RUN_ONLY_USB', '1')

        elif panel == 'PT500GT01-1' or \
             panel == 'T215HVN05.1' or \
             panel == 'V400HJ6-PE1-C3':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1920_1080")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '0')

        elif panel == 'HV430FHB-N1A' or \
             panel == 'HV490FHB-N8L' or \
             panel == 'HV430QUB-N1D' or \
             panel == 'HV430QUB-N1A' or \
             panel == 'HV430FHB-N1K':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_CHAOYE_HV430FHB_N40")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '3')
                panelstr += self.get_macro_line('CVT_EN_FORCE_FREE_RUN', '1')
                panelstr += self.get_macro_line('CVT_DEF_SSC_LVDS_VALUE', '0')

        elif panel == 'HV490FHB-N8K':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1920_1080")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '3')
                panelstr += self.get_macro_line('CVT_EN_FORCE_FREE_RUN_ONLY_USB', '1')
                panelstr += self.get_macro_line('CVT_DEF_SSC_LVDS_VALUE', '0')

        elif panel == 'LC430DUY-SHA1':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1920_1080")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '0')
                panelstr += self.get_macro_line('CVT_EN_SET_FORCEFREERUN_ONLY_ATV', '1')
                panelstr += self.get_macro_line('CVT_DEF_SSC_LVDS_VALUE', '0')

        elif panel == 'V500DJ6-QE1' or \
             panel == 'CV500U1-T01-V02' or \
             panel == 'CV500U1-T01-V03' or \
             panel == 'V50DDJ6-QE1':
                panelstr += self.get_macro_line(self.panel_macro_name, "ID_PNL_General_1920_1080")
                panelstr += self.get_macro_line(self.panel_mirror_macro_name, '0')
                panelstr += self.get_macro_line('CVT_DEF_PANEL_ID', '4')

        else:
            raise RuntimeError("警告: panel_config.json文件中，还未配置添加 " + panel)
        return panelstr

    def get_logo_macro(self):
        """
        logo
        :return:
        """
        if self._logo_type == "______":
            logostr = self.get_macro_line(self.logo_macro_name, "ID_LOGO_NONE")
        elif self._logo_type == "TMSS_FULL_HD_LED_TV":
            logostr = self.get_macro_line(self.logo_macro_name, "ID_LOGO_CHAOYE_TMSS_FHD")
        elif self._logo_type == "JOIIII":
            logostr = self.get_macro_line(self.logo_macro_name, "ID_LOGO_CHAOYE_JOIII")
        elif self._logo_type == "AMAZ":
            logostr = self.get_macro_line(self.logo_macro_name, "ID_LOGO_CHAOYE_AMAZ_LIFE")
        else:
            logostr = self.get_macro_line(self.logo_macro_name, "ID_LOGO_CHAOYE_" + self._logo_type)

        return logostr

    def get_keypad_macro(self):
        if 'VIDEOCON客户按键板' in self._order_comment:
            keypadstr = self.get_macro_line(self.keypad_macro_name, "KEYPAD_CHAOYE_PIN_TO_PIN_VEDIOCON")
        else:
            keypadstr = self.get_macro_line(self.keypad_macro_name, "KEYPAD_CHAOYE_PIN_TO_PIN_9202")
        return keypadstr

    def get_remote_macro(self):
        """
        遥控器
        :return:
        """
        mark, data, message = self.ir_resource_check()
        remote_id = data
        remote_macro = "//ir\n"
        remote_macro += self.get_macro_line(self.ir_macro_name, remote_id)
        return remote_macro

    def get_language_macro(self):
        """
        语言
        :return:
        """
        language_macro = "//language\n"

        default_language, language_option, is_ng = self.language_resource_check()
        language_macro += self.get_macro_line(self.default_language_macro_name, default_language)

        for language in language_option:
            language_macro += self.get_macro_line(language, "1")

        return language_macro

    def get_other_macro(self):
        """
        其他
        :return:
        """
        other_macro = "//production mode\n"
        if self._shipping_mode == '整机':
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_FAC_RESET", "1")
        else:
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_FAC_SKD_RESET", "1")
        other_macro += "//other\n"
        if "二次记忆开关" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_FAC_RESET_POWERON_MODE_LAST", "1")
        if ("抓图" in self._order_comment) and ("可以清除" in self._order_comment):
            other_macro += self.get_macro_line("CVT_EN_USER_RESET_SAVE_CAPTURE_LOGO", "0")
        if ("抓图" in self._order_comment) and ("工作清除" in self._order_comment):
            other_macro += self.get_macro_line("CVT_EN_USER_RESET_SAVE_CAPTURE_LOGO", "0")
        if ("抓图" in self._order_comment) and ("要清除" in self._order_comment):
            other_macro += self.get_macro_line("CVT_EN_USER_RESET_SAVE_CAPTURE_LOGO", "0")
        if ("抓图" in self._order_comment) and ("不清除" in self._order_comment):
            other_macro += self.get_macro_line("CVT_EN_USER_RESET_SAVE_CAPTURE_LOGO", "1")
        if self._shipping_mode == "显示器":
            other_macro += self.get_macro_line("CVT_DEF_INPUT_SOURCE_TYPE", "UI_INPUT_SOURCE_RGB")
            other_macro += self.get_macro_line("CVT_EN_ONLY_VGA_SOURCE_BY_PASSWD", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_SET_POWER_STANDBY_WHEN_ONLY_VGA_BY_PASSWD",
                                               "1//menu2580 open other source")
            other_macro += self.get_macro_line("CVT_DEF_POWERON_MODE", "ID_POWERON_MODE_ON")

        if self._logo_type == "AKARI_2":
            other_macro += self.get_macro_line("CUS_SPECIAL_REQUEST_TYPE", "SPECIAL_REQUEST_TYPE_INDONESIA_AKARI")
            
        if "打开EQ" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_EQ_TREBLE_BASS_MODE", "TRUE")

        if "图文" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_TTX", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_NICAM", "TRUE")
        if "CEC" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_CEC", "TRUE")
        if "ARC" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_ARC", "TRUE")

        if "上电开机" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_FAC_RESET_POWERON_MODE_ON","1")

        if "电子屏贴" in self._order_comment:
            other_macro += self.get_macro_line("CVT_DEF_EPOP_TYPE", "EPOP_TYPE_CHAOYE")
            other_macro += self.get_macro_line("CVT_DEF_EPOP_VALUE", "0")
            other_macro += self.get_macro_line("CVT_EN_SECOND_EPOP_DYNAMIC_PIC", "0")
            if self._logo_type == "BLUE":
                other_macro += self.get_macro_line(
                    "CVT_DEF_OSD_BMP_BIN",
                    "\"code/tv-ap/dvb/ui_cvt_960/ui2/res960x540x565/osdcomposer/osdbin/ZUI_bitmap_chaoye_EPOP_JVC\"")
            elif self._logo_type == "AMAZ":
                other_macro += self.get_macro_line(
                    "CVT_DEF_OSD_BMP_BIN",
                    "\"code/tv-ap/dvb/ui_cvt_960/ui2/res960x540x565/osdcomposer/osdbin/ZUI_bitmap_chaoye_EPOP_AMAZ\"")
            elif self._logo_type == "PATTERS":
                other_macro += self.get_macro_line(
                    "CVT_DEF_OSD_BMP_BIN",
                    "\"code/tv-ap/dvb/ui_cvt_960/ui2/res960x540x565/osdcomposer/osdbin/ZUI_bitmap_chaoye_EPOP_PATTERS\"")
        if "拷贝到USB" in self._order_comment:
            other_macro += self.get_macro_line("CVT_EN_TWO_USB_COPY", "TRUE")
        if "按VIDEOCON客户标准" in self._order_comment:
            other_macro += self.get_macro_line("CVT_DEF_PQ_TYPE", "ID_PQ_PT320AT011_32DN4S_SY18002")
            other_macro += self.get_macro_line("CVT_DEF_PANEL_NAME", "\""+self._panel_type+"\"")
            other_macro += self.get_macro_line("CUS_SPECIAL_REQUEST_TYPE", "SPECIAL_REQUEST_TYPE_VIDEOCON")
            other_macro += self.get_macro_line("CVT_EN_USER_RESET_SAVE_CAPTURE_LOGO", "0")
            other_macro += self.get_macro_line("CVT_DEF_SOUND_MODE", "4//user")
            other_macro += self.get_macro_line("CVT_DEF_SETBASS_RATIO", "50")
            other_macro += self.get_macro_line("CVT_DEF_SET_TREBLE_RATIO", "50")
            other_macro += self.get_macro_line("CVT_EN_BASS_TREBLE_RATIO_MAX", "1")
            other_macro += self.get_macro_line("CVT_EN_LIMIT_TREBLE_BASS_50_TO_100", "1")
            other_macro += self.get_macro_line("CVT_EN_PIC_MODE_ECO", "1")
            other_macro += self.get_macro_line("CVT_DEF_ECO_MODE_BACKLIGHT", "50")
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_HOME_MODE_USE_INDEP_BACLIGHT", "1")
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_FACTORY_MENU_PANEL_INFO", "0")
            other_macro += self.get_macro_line("CVT_DEF_BLUE_SCREEN_VALUE", "0")
            other_macro += self.get_macro_line("CVT_DEF_FAC_GAMMA_VALUE", "GAMMA_WHOLE_BRIGHTER")

        other_macro += "//END\n"
        return other_macro
