import re
from customers.customer_chaoye.chaoye_ruler import ChaoYeRuler


class Ruler(ChaoYeRuler):
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

    board_macro_name = "CVT_DEF_BOARD_TYPE"
    chip_macro_name = "CVT_DEF_CHIP_TYPE"
    flash_macro_name = "CVT_DEF_FLASH_SIZE"
    ci_macro_name = "CVT_DEF_CI_TYPE"
    wifi_macro_name = "CVT_DEF_WIFI_TYPE"
    tuner_macro_name = "CVT_DEF_SECOND_TUNER_TYPE"
    pwm_macro_name = "CVT_DEF_PWM_REF_MAX"

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

    def get_country_name(self):
        country_dict = self.get_config_res('country')
        country_str = ""
        try:
            country_str = country_dict["default_country"][self._country_code]
            country_str = country_str.replace("ID_COUNTRY_", "")
        except KeyError:
            raise RuntimeError("警告： country_config.json文件中，还未配置添加" + self._country_code)

        return country_str

    def get_ocs_require(self):
        """
        强制要求实现，获取model id的配置内容
        :return:
        """
        model_id_head = '#elif(IsModelID(' + self.get_ocs_modelid() + '))' + '\n'

        ocs_macro = self.get_macro_line("CVT_DEF_OCS_ID","\"CP"+self.ocs_demand.ocs_number+"\"")
        hardware_macro = self.get_hardware_macro()
        sound_macro = self.get_sound_macro()
        panel_macro = self.get_panel_macro()
        logo_macro = self.get_logo_macro()
        remote_macro = self.get_remote_macro()
        language_macro = self.get_language_macro()
        other_macro = self.get_other_macro()

        software_config = model_id_head + ocs_macro + hardware_macro + sound_macro + panel_macro + logo_macro + \
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
        hardware_dict = self.get_config_res("hardware")

        if self._hardware_key in list(hardware_dict):
            hardware_info = hardware_dict[self._hardware_key]
            
            board_type = hardware_info['board_type']
            chip_type = hardware_info['chip_type']
            flash_size = hardware_info['flash_size']
            ci_type = hardware_info['ci_type']
            wifi_type = hardware_info['wifi_type']
            tuner_type = hardware_info['tuner_type']
            current_ref = hardware_info['current_ref']

            hardware_macro = "//board & chip & wifi & tuner & ci needs\n"
            hardware_macro += self.get_macro_line(self.board_macro_name, board_type)
            hardware_macro += self.get_macro_line(self.chip_macro_name, chip_type)
            hardware_macro += self.get_macro_line(self.flash_macro_name, flash_size)
            hardware_macro += self.get_macro_line(self.ci_macro_name, ci_type)
            hardware_macro += self.get_macro_line(self.wifi_macro_name, wifi_type)
            hardware_macro += self.get_macro_line(self.tuner_macro_name, tuner_type)
            hardware_macro += self.get_macro_line(self.pwm_macro_name, str(current_ref))

            return hardware_macro
        else:
            raise RuntimeError("警告: hardware_config.json文件中，还未配置添加 " + self._hardware_key)

    def get_sound_macro(self):
        """
        sound
        :return:
        """
        board_name = self._board_type
        machine_size = re.sub("\D", "", self._machine_type)[:2]
        sound_macro = "//Sound\n"

        machine_name = self._machine_type.upper()
        hornflag = machine_name.find('S')!=-1 or machine_name.find('L')!=-1
        # hornflag < 0 #普通喇叭
        # horflag  > 0 #音响喇叭

        if str(board_name) == "TP.MT5510S.PB802":
            sound_macro += self.switch_5510_PB802_sound(machine_size, int(hornflag))
        elif str(board_name) == "TP.MT5510I.PB801":
            sound_macro += self.switch_5510_PB801_sound(machine_size, int(hornflag))
        elif str(board_name) == "T.MT5510S.82":
            sound_macro +=  self.switch_5510_82_sound(machine_size, int(hornflag))
        elif str(board_name) == "T.MT5510I.81":
            sound_macro +=  self.switch_5510_81_sound(machine_size, int(hornflag))
        else:
            raise RuntimeError("警告:未知的机型, CVT_DEF_SOUND_TYPE 未有对应值!!")
        return sound_macro

    def switch_5510_82_sound(self, sizenum, hornflag):
        if hornflag <= 0:
            if int(sizenum) >= 27 and int(sizenum) <= 43:
                pass
            elif int(sizenum) > 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_82_CHAOYE_12V8R8W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "190")
            else:
                soundstr = "SOUND_ERROR"
        else:
            pass
        return soundstr

    def switch_5510_81_sound(self, sizenum, hornflag):
        if hornflag <= 0:
            if int(sizenum) >= 27 and int(sizenum) <= 43:
                pass
            elif int(sizenum) > 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_5510_81B_CHAOYE_12V8R8W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "190")
            else:
                soundstr = "SOUND_ERROR"
        else:
            pass
        return soundstr


    def switch_5510_PB802_sound(self, sizenum, hornflag):
        if hornflag <= 0:
            if int(sizenum) >= 27 and int(sizenum) <= 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB802_CHAOYE_12V8R7W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "190")
            elif int(sizenum) > 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB802_CHAOYE_12V8R8W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "190")
            else:
                soundstr = "SOUND_ERROR"
        else:
            if int(sizenum) >= 27 and int(sizenum) <= 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB802_CHAOYE_12V8R5W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "80")
            elif int(sizenum) > 43:
                soundstr = self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB802_CHAOYE_12V8R6W5")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "80")
            else:
                soundstr = "SOUND_ERROR"
        return soundstr

    def switch_5510_PB801_sound(self, sizenum, hornflag):
        soundstr = ''
        if hornflag <= 0: #普通喇叭
            if int(sizenum) >= 30 and int(sizenum) <= 43:
                soundstr += self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB801_CHAOYE_12V8R7W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "190")
            elif int(sizenum) > 43:
                soundstr += self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB801_CHAOYE_12V8R8W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "190")
            else:
                soundstr += "SOUND_ERROR"
        else:
            if int(sizenum) >= 30 and int(sizenum) <= 43:
                soundstr += self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB801_CHAOYE_12V8R5W")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "80")
            elif int(sizenum) > 43:
                soundstr += self.get_macro_line(self.aq_macro_name,
                                               "ID_SOUND_AMP_PB801_CHAOYE_12V8R6W5")
                soundstr += self.get_macro_line("CVT_EN_LINE_OUT", "FALSE")
                soundstr += self.get_macro_line("CVT_EN_HPF", "1")
                soundstr += self.get_macro_line("CVT_DEF_HPF_FC", "80")
            else:
                soundstr += "SOUND_ERROR"
        return soundstr


    def get_panel_macro(self):
        """
        panel
        :return:
        """
        panel_dict = self.get_config_res("panel")

        panel_name = self._panel_type
        panel_name = panel_name.strip()
        panel_name = panel_name.replace(' ', '-')
        panel_name = panel_name.replace('(', '-')
        panel_name = panel_name.replace(')', '')

        if panel_name in list(panel_dict):
            panel_info = panel_dict[panel_name]
            panel_type = panel_info['panel_type']
            panel_mirror = panel_info['mirror']

            panel_macro = "//panel\n"
            panel_macro += self.get_macro_line(self.panel_macro_name, str(panel_type))
            panel_macro += self.get_macro_line(self.panel_mirror_macro_name, str(panel_mirror))

            if panel_name == "V320BJ8-Q01":
                panel_macro += self.get_macro_line("CVT_DEF_LVDS_SSC_FREQ","30")
                panel_macro += self.get_macro_line("CVT_DEF_LVDS_SSC_RANGE","30")
            elif panel_name == "T430HVN01.0":
                panel_macro += self.get_macro_line("CVT_DEF_PQ_TYPE","ID_PQ_CHAOYE_T430HVN01_0_K19014")
                panel_macro += self.get_macro_line("CVT_DEF_PQBIN_TYPE","ID_PQBIN_CHAOYE_T430HVN01_0")
            elif panel_name == "CV500U1-T01-V02" or panel_name == "CV500U1-T01-V03":
                panel_macro += self.get_macro_line("CVT_DEF_PQBIN_TYPE","ID_PQBIN_CHAOYE_CV500U1_T01_V03")          
            return panel_macro
        else:
            raise RuntimeError("警告: panel_config.json文件中，还未配置添加 " + self._panel_type)
            return panel_macro

    def get_logo_macro(self):
        """
        logo
        :return:
        """
        logo_macro = ''
        if (self._logo_type is None) or (self._logo_type == 'NOLOGO') or (self._logo_type == '------'):
            return logo_macro
        else:
            logo_type = self._logo_type
            logo_type = logo_type.upper()
            logo_type = logo_type.replace("-", "_")
            logo_type = logo_type.replace(" ", "_")
            logo_type = logo_type.replace('蓝屏', 'BLUE')

            logo_macro = "//logo\n"
            self.get_macro_line(self.logo_macro_name, "ID_LOGO_CHAOYE_" + logo_type)
            return logo_macro

    def get_remote_macro(self):
        """
        遥控器
        :return:
        """
        remote_macro = ''

        remote_dict = self.get_config_res("ir")
        if self._remote_type is None:
            return remote_macro
        else:
            remote_key = self._remote_type[0:9]
            try:
                remote_id = remote_dict[remote_key]
                remote_macro = "//ir\n"
                remote_macro += self.get_macro_line(self.ir_macro_name, remote_id)
                if remote_key == "2618-EDR0":
                    remote_macro +=self.get_macro_line("CVT_DEF_IR2_TYPE", "ID_IR_CHAOYE_IPTV_EU_2618_EDR0_RC03")
                    remote_macro +=self.get_macro_line("CVT_DEF_IR3_TYPE", "ID_IR_CHAOYE_IPTV_EU_2618_EDR0_RC17")

            except KeyError:
                raise RuntimeError("警告: ir_config.json文件中，还未配置添加 " + remote_key)

            return remote_macro

    def get_language_macro(self):
        """
        语言
        :return:
        """
        flag_default = '(默认)'
        language_dict = self.get_config_res("language")
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
            language_macro += self.get_macro_line(self.default_language_macro_name,
                                                  language_default_dict[language_default])
        except KeyError:
            raise RuntimeError("警告: language_config.json文件中，还未配置添加 " + language_default)

        for i in range(0, len(language_option)):
            try:
                language_macro += self.get_macro_line(language_option_dict[language_option[i]], "TRUE")
            except KeyError:
                raise RuntimeError("警告: language_config.json文件中，还未配置添加 " + language_option[i])

        return language_macro

    def get_other_macro(self):
        """
        其他
        :return:
        """
        irstr = self._remote_type[0:9]
        irbarch = self._remote_type[5:7]
        curtemp = self.get_country_name()
        logotemp = self._logo_type().upper()
        logotemp = logotemp.replace(" ", "_")
        logotemp = logotemp.replace("-", "_")        
        commonflag = 0


        other_macro = "//Other\n"

        if logotemp == 'JVC' and (curtemp == 'COLOMBIA' or curtemp == 'PANAMA'):
            other_macro += self.get_macro_line("CVT_EN_APP_ESHARE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APK_JVC_MARKET", "TRUE")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT_COL")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_COL")
            other_macro += self.get_macro_line("CVT_DEF_LAUNCHER_SKIN_TYPE", "ID_LAUNCHER_SKIN_CYAOYE_JVC")
            other_macro += self.get_macro_line("CVT_DEF_LAUNCHER_BATCH_CODE", "BEDghHsrgjCZIild")
            other_macro += "//Netflix\n"
            other_macro += self.get_macro_line("CVT_EN_GOOGLE_PLAY_SERVICES_FOR_553", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_NETFLIX_4_16", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_SKIP_NETFLIX_4_16_UPDATE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_GOOGLE_PLAY_STORE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_HKC_DATA_OTA", "TRUE")

            commonflag = 1
        elif logotemp == 'JVC' and curtemp == 'ECUADOR':
            other_macro += self.get_macro_line("CVT_EN_APP_ESHARE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APK_JVC_MARKET", "TRUE")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_REUSE_KEY_CC_JVC")
            other_macro += self.get_macro_line("CVT_DEF_LAUNCHER_SKIN_TYPE", "ID_LAUNCHER_SKIN_CYAOYE_JVC")
            other_macro += self.get_macro_line("CVT_DEF_LAUNCHER_BATCH_CODE", "BEDghHsrgjCZIild")
            other_macro += "//Netflix"
            other_macro += self.get_macro_line("CVT_EN_GOOGLE_PLAY_SERVICES_FOR_553", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_NETFLIX_4_16", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_SKIP_NETFLIX_4_16_UPDATE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_GOOGLE_PLAY_STORE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_HKC_DATA_OTA", "TRUE")

            commonflag = 1

        elif (logotemp == 'FOX_X' and curtemp == 'SERBIA') or \
             (logotemp == 'STELL' and curtemp == 'SERBIA'):

            other_macro += self.get_macro_line("CVT_EN_APP_APTOIDE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APK_CHAOYE_RRO_MEDIACENTER_SERBRA", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APK_CHAOYE_RRO_TVSETTING_SERBRA", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APK_CHAOYE_RRO_TVSETTING_JVC", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APK_CHAOYE_RRO_MEDIA_CENTER", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APK_CHAOYE_RRO_MEDIA_PLAYER", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_WFD", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_ESHARE", "TRUE")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_HOTEL_MODE")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")
            other_macro += self.get_macro_line("CVT_EN_HOTEL_MODE", "TRUE")

            commonflag = 1
        elif logotemp == 'FUJITA' and curtemp == 'MADAGASCAR':

            other_macro += self.get_macro_line("CVT_EN_WFD", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_SKYPE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_TWITTER", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_GOOGLE_PLAY_STORE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_FACEBOOK", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_YOUTUBE_TV", "TRUE")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")

            commonflag = 1

        elif logotemp == 'DAEWOO_2' and irstr == '2627_EIR0':
            other_macro += self.get_macro_line("CHAOYE_REQUIRED_MODE", "CHAOYE_REQUIRED_FOR_DEAWOO_UI")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_2627_EIR0_DEAWOO")

            commonflag = 1
        elif logotemp == 'DAEWOO_2' and irstr == '2627_EAR0':
            other_macro += self.get_macro_line("CHAOYE_REQUIRED_MODE", "CHAOYE_REQUIRED_FOR_DEAWOO_UI")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_US_REUSE_KEY_CC_DAEWOO")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_US_ATSC")
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_ATSC_CC_TYPE", "TRUE")            

            commonflag = 1
        elif logotemp == 'DAEWOO_2' and irstr == '2627_EDR0' and curtemp == 'MALAYSIA':

            other_macro += self.get_macro_line("CHAOYE_REQUIRED_MODE", "CHAOYE_REQUIRED_FOR_DEAWOO_UI")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_2627_EDR0_DAEWOO")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")


            commonflag = 1
        elif logotemp == 'DAEWOO_2' and irstr == '2627_EDR0' and curtemp == 'PANAMA':

            other_macro += self.get_macro_line("CVT_EN_PANAMA_CHANNEL_TABLE_DAEWOO", "1")
            other_macro += self.get_macro_line("CHAOYE_REQUIRED_MODE", "CHAOYE_REQUIRED_FOR_DEAWOO_UI")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_2627_EDR0_DAEWOO")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT_COL")

            commonflag = 1
        elif (logotemp == 'HAMBER'  and curtemp == 'RUSSIA') or \
             (logotemp == 'POLAR_1366' and curtemp == 'RUSSIA') or \
             (logotemp == 'POLAR_1920'  and curtemp == 'RUSSIA')or \
             (logotemp == 'POLARLINE_2' and curtemp == 'RUSSIA' ) or \
             (logotemp == 'SAMTRON' and curtemp == 'RUSSIA') or \
             (logotemp == 'NESONS' and curtemp == 'RUSSIA') or \
             (logotemp == 'NEKO' and curtemp == 'RUSSIA'):

            other_macro += self.get_macro_line("CVT_DEF_LCN_SWITCH", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_BOARDINIT_IMPORT_CHANNEL", "TRUE")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")
            if '酒店模式' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_HOTEL_MODE", "TRUE")
                other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_RUSSIA_POLAR_HOTEL")
            else:
                other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_RUSSIA_POLAR")
            other_macro += "//APP\n"
            other_macro += self.get_macro_line("CVT_EN_WFD", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_APTOIDE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_SKYPE", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_POLAR_YOUTUBETV", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_MX_PLAYER", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_VLC_PLAYER", "TRUE")
            other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_PLANER_TV", "TRUE")

            commonflag = 1
        elif logotemp == 'ASANO_4' and curtemp == 'RUSSIA':
            other_macro += self.get_macro_line("CHAOYE_REQUIRED_MODE", "CHAOYE_REQUIRED_FOR_ASANO_WILDRED")
            other_macro += self.get_macro_line("CVT_EN_CUSTOMER_DEVICE_INFO", "TRUE")
            other_macro += self.get_macro_line("CVT_DEF_CUSTOMER_STR_DEVICE", "ASANO_Shell_5510")
            other_macro += self.get_macro_line("CVT_DEF_CUSTOMER_MODEL_NAME", "28LH1010T")
            if '酒店模式' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_HOTEL_MODE", "TRUE")
                other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_RUSSIA_POLAR_HOTEL")
            else:
                other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_RUSSIA_POLAR")

            commonflag = 1
        elif logotemp == 'PRESTIGIO' and curtemp == 'BELARUS':
            other_macro += self.get_macro_line("CVT_EN_WFD", "1")
            other_macro += self.get_macro_line("CVT_EN_APP_APTOIDE", "1")
            other_macro += self.get_macro_line("CVT_DEF_LCN_SWITCH", "1")
            other_macro += self.get_macro_line("CVT_EN_UPGRADE_ENTER_AGING", "1")
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_WB_IMPORT", "0")
            other_macro += self.get_macro_line("CVT_EN_UPGRADE_REBOOT", "0")
            other_macro += self.get_macro_line("CVT_EN_BOARDINIT_IMPORT_CHANNEL", "1")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_RUSSIA_PRESIGO")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")

            commonflag = 1
        elif logotemp == 'SUPER_GENERAL' and irstr == '26A9-EDR0':
            other_macro += self.get_macro_line("CVT_EN_WFD", "1")
            other_macro += self.get_macro_line("CVT_EN_APP_APTOIDE", "1")
            other_macro += self.get_macro_line("CVT_EN_APP_TVASSISTANT_CVTE", "1")
            other_macro += self.get_macro_line("CVT_EN_APP_GAIA_10", "0")
            other_macro += self.get_macro_line("CVT_EN_APP_GAIA_20", "1")
            other_macro += self.get_macro_line("CVT_EN_APP_GAIA_AI", "0")
            other_macro += self.get_macro_line("CVT_EN_APP_ZEASN_OCS", "0")
            other_macro += self.get_macro_line("CVT_DEF_LAUNCHER_BATCH_CODE", "\"CVTE_TV_STARK\"")
            other_macro += self.get_macro_line("CVT_DEF_POWER_ON_TV_STATUS", "ID_TV_STATUS_HOME_TV")
            other_macro += self.get_macro_line("CVT_DEF_LAUNCHER_TYPE", "ID_LAUNCHER_HIGH_END_SUPER_GENERAL")
            other_macro += self.get_macro_line("CVT_DEF_LAUNCHER_SKIN_TYPE", "ID_LAUNCHER_SKIN_30_GAIA_20_CHAOYE_SUPER_GENERAL")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_HOTEL_MODE_SUPER_GENERAL_GAIA")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")
            other_macro += self.get_macro_line("CVT_EN_HOTEL_MODE", "1")

            commonflag = 1
        elif irbarch == "ED" and curtemp == 'RUSSIA':
            other_macro += self.get_macro_line("CVT_EN_WFD", "1")
            other_macro += self.get_macro_line("CVT_DEF_LCN_SWITCH", "1")
            other_macro += self.get_macro_line("CVT_EN_BOARDINIT_IMPORT_CHANNEL", "1")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_RUSSIA_POLAR")

        elif irbarch == "ED" and curtemp == 'AZERBAIJAN':
            other_macro += self.get_macro_line("CVT_EN_WFD", "1")
            other_macro += self.get_macro_line("CVT_DEF_POWER_ON_TV_STATUS", "ID_TV_STATUS_MEMORY_FIRST_ANDROID")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_AZERBAIJAN")

        elif irbarch == "ED" or irbarch == "UD":
            other_macro += self.get_macro_line("CVT_EN_WFD", "1")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_EU_DVBT")

            if ('电子标签' in self._order_comment) and logotemp == 'SUNNY':
                other_macro += self.get_macro_line("CVT_EN_STORE_MODE", "1")
                other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_SUNNY_STORE_MODE")
              
            elif '酒店模式' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_HOTEL_MODE", "TRUE")
                other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU_HOTEL_MODE")
            else:
                other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_EU")
        elif irbarch == "EI":
            other_macro += self.get_macro_line("CVT_EN_WFD", "1")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_REUSE_KEY_CC")

        elif irbarch == "EA":
            other_macro += self.get_macro_line("CVT_EN_WFD", "1")
            other_macro += self.get_macro_line("CVT_EN_CHAOYE_ATSC_CC_TYPE", "1")
            other_macro += self.get_macro_line("CVT_DEF_MARKET_REGION", "ID_MARKET_REGION_US_ATSC")
            other_macro += self.get_macro_line("CVT_DEF_MENU_CONFIG_XML_TYPE", "ID_MENU_CONFIG_XML_CHAOYE_US") 

        if commonflag == 0:
            #解析批注

            if '时间' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_SHOW_TOTAL_RUNNING_TIME", "1")
            if '记忆开机' in self._order_comment:
                other_macro += self.get_macro_line("CVT_DEF_POWERON_MODE", "ID_POWERON_MODE_LAST")
            if 'YOUTUBE' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_YOUTUBE_TV", "1")
            if 'GOOGLE PLAY' in self._order_comment \
            or 'GOOGLE-PLAY' in self._order_comment \
            or 'PLAYSTORE' in self._order_comment \
            or 'Googleplay' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_GOOGLE_PLAY_STORE", "1")
            else:
                other_macro += self.get_macro_line("CVT_EN_APP_APTOIDE", "1")

            if 'FACEBOOK' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_FACEBOOK", "1")
            if 'SKYPE' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_SKYPE", "1")
            if 'NETFLIX' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_NETFLIX_TV", "1")
            if 'TWITTER' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_TWITTER", "1")
            if 'E-SHARE' in self._order_comment or 'ESHARE'in self._order_comment or 'E-share'in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_ESHARE", "1")
            if 'KODI' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_KODI", "1")
            if 'SMART PRO IPTV' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_APP_CHAOYE_SMART_PRO_IPTV", "1")
            if 'LCN默认打开' in self._order_comment or '打开LCN' in self._order_comment:
                other_macro += self.get_macro_line("CVT_DEF_LCN_SWITCH", "1")
            if 'BISS' in self._order_comment:
                other_macro += self.get_macro_line("CVT_EN_IMPORT_BISS_KEY", "1")
        other_macro += "//END\n"
        return other_macro
