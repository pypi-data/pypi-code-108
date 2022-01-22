import os
import re
import sys


sys.path.insert(1,"/ssd2/zhanghonghai/codes/pyocs/pyocs")

from customers.customer_sqy.user_bom_get_hardware_data_config import get_bom_param
_space_ = 55

#--------------------------------------------------------
#  料号库
#  相同料号的订单，硬件配置包括占空比等全都一样，统计现有的料号可以维护一个料号库配置，每次直接调用
#--------------------------------------------------------
def createbom(bomnum):
    return get_bom_param(bomnum)[:-1]

#--------------------------------------------------------
#  keypad
#--------------------------------------------------------
def createkeypad(keypad):
    if '5' in keypad:
        keypadstr = "#define CVT_DEF_KEYPAD_TYPE".ljust(_space_)+"ID_KEYPAD_SQY_5KEY_DEFAULT"
    if '7' in keypad:
        keypadstr = "#define CVT_DEF_KEYPAD_TYPE".ljust(_space_)+"ID_KEYPAD_SQY_7KEY_DEFAULT"
    return keypadstr

#--------------------------------------------------------
#  panel
#--------------------------------------------------------
def createpanel(panel):
    if  panel != '':
        panelstr = ("#define CVT_DEF_SQY_PNL_TYPE".ljust(_space_)+"ID_SQY_PNL_CONFIG_" + panel + "")
    else:
        panelstr == "PANEL_ERROR"
    return panelstr

#--------------------------------------------------------
#  ir
#  REMARK：ir 处理遥控器编号和宏映射关系
#--------------------------------------------------------
def createir(ir):
    switcher = {
        "RC057A-10" : "#define CVT_DEF_IR_TYPE".ljust(_space_)+"ID_IR_SQY_EU_RC057A_10MOUSE",
        "RC057A-6"  : "#define CVT_DEF_IR_TYPE".ljust(_space_)+"ID_IR_SQY_AM_RC057A_6",
        "RC057A-4"  : "#define CVT_DEF_IR_TYPE".ljust(_space_)+"ID_IR_SQY_AP_RC057A_4",
        "RC2063-13" : "#define CVT_DEF_IR_TYPE".ljust(_space_)+"ID_IR_SQY_EU_RC2063_13",
        "XK-106A"   : "#define CVT_DEF_IR_TYPE".ljust(_space_)+"ID_IR_SQY_EU_VISION",
    }
    sqy_ir_type = ''
    if "RC057A-10"   in ir:
        sqy_ir_type = "RC057A-10"
    elif "RC057A-6"  in ir:
        sqy_ir_type = "RC057A-6"
    elif "RC057A-4"  in ir:
        sqy_ir_type = "RC057A-4"
    elif "RC2063-13" in ir:
        sqy_ir_type = "RC2063-13"
    elif "XK-106A"   in ir:
        sqy_ir_type = "XK-106A"


    return switcher.get(sqy_ir_type,"IR_ERROR")


#--------------------------------------------------------
#  def language
#--------------------------------------------------------
def createdeflang(def_lang):
    deflangstr = switch_defalut_lang(def_lang)
    return deflangstr

#--------------------------------------------------------
#  osd language
#--------------------------------------------------------
def createosdlanguage(osd_lang):
    #得到分割后的语言list
    langlist = osd_lang.split('、')

    for index in range(0, len(langlist)):
        langlist[index] = langlist[index].strip()

    #循环取得其他语言定义
    langstr = ""
    for i in langlist:
        langstr += switch_lang(i)
    return langstr[:-1]

def switch_defalut_lang(defalutlang):
    if defalutlang != '':
        lang_str = "ID_LANGUAGE_" + change_lang(defalutlang)
        return ("#define CVT_DEF_LANGUAGE_SELECT".ljust(_space_) + lang_str + "")
    else:
        return "DEFAULT_LANG_ERROR"

def switch_lang(lang):
    if lang != '':
        lang_str = "#define CVT_EN_LANG_" + change_lang(lang)
        return (lang_str.ljust(_space_) +"1\n")
    else:
        return "LANG_ERROR"

def change_lang(lang):
    switcher = {

        "英":        "ENGLISH_US",
        "英语":      "ENGLISH_US",
        "法":        "FRENCH_FR",
        "德":        "GERMAN_DE",
        "俄":        "RUSSIAN_RU",
        "意":        "ITALIAN_IT",
        "阿拉伯":    "ARABIC_EG",
        "保加利亚":  "BULGARIAN_BG",
        "希腊":      "CZECH_CS",
        "阿尔巴尼亚": "ALBANIAN_SQ",
        "马其顿":    "MACEDONIAN_MK",
        "意大利":    "ITALIAN_IT",
        "罗马尼亚":  "ROMANIAN_RO",
        "西":        "SPANISH_ES",
        "西班牙":    "SPANISH_ES",
        "葡":        "PORTUGUESE_PT",
        "葡萄牙":    "PORTUGUESE_PT",
        "斯洛文尼亚": "SLOVENIAN_SL",
        "克罗地亚":  "CROATIAN_HR",
        "匈牙利":    "HUNGARIAN_HU",
        "塞尔维亚":  "SERBIAN_SR",
        "土耳其":    "TURKISH_TR",
        "波斯":      "FARSI_IR",
        "马来西亚":  "MALAYSIA_MY",
        "中":        "CHINESE_CN",
        "泰":        "THAI_TH",
    }
    return switcher.get(lang,"LANG_ERROR")

def switch_country_name(country):
    switcher = {
        "印度"    : "INDIA",
        "俄罗斯"  : "RUSSIA",
        "乌克兰"  : "UKRAINE",
        "西班牙"  : "SPAIN",
        "波兰"    : "POLAND",
        "肯尼亚"  : "KENYA",
    }
    return switcher.get(country,"COUNTRY_NAME_ERROR")


def createcountry(country):
    if country != '':
        return ("#define CVT_DEF_COUNTRY_SELECT".ljust(_space_)+"ID_COUNTRY_" + switch_country_name(country))
    else:
        return ("COUNTRY_ERROR")

#--------------------------------------------------------
#  sound
#  这里需要跟进自己客户的声音配置特性来写宏映射关系，如下是举例
#--------------------------------------------------------
#TODO:这里可以直接获取默认的声音曲线文件
def createsound(board, sound):

    if str(board) == "TP.SK508S.PB801":
        if sound == "8R8W":
            soundstr =  "#define CVT_DEF_SOUND_TYPE".ljust(_space_)+"ID_SOUND_AD52050_COMMON_DEFAULT_12V8R8W\n"
        else:
            soundstr = "SOUND_ERROR"
    else:
        soundstr = "SOUND_ERROR"
    return soundstr

#--------------------------------------------------------
#  miracast
#  这部分需要根据你的客户和方案实际情况和配置，配合表格来做对应的宏。默认公共已打开的宏可以不配
#--------------------------------------------------------
def createmiracast(miracast):
    if miracast == "Miracast":
        mirastr = "#define CVT_EN_APK_MIRACAST".ljust(_space_)+"1"
    elif miracast == "Eshare":
        mirastr = "#define CVT_EN_APPLIST_ESHARE".ljust(_space_)+"1"
    return mirastr


#--------------------------------------------------------
#  app other
#  根据自己客户的APK映射关系来添加配置
#--------------------------------------------------------
def createappother(applist):

    appotherstr = ""
    if "youtube" in applist.lower() :
        appotherstr += "#define CVT_EN_APP_SQY_YOUTUBE".ljust(_space_)+"1\n"
    if "face" in applist.lower():#facebook
        appotherstr += "#define CVT_EN_APP_FACE_BOOK".ljust(_space_)+"1\n"
    if "netflix" in applist.lower():
        appotherstr += "#define CVT_EN_APP_SQY_NETFLIX_4_16".ljust(_space_)+"1\n"
    if "twitter" in applist.lower():
        appotherstr += "#define CVT_EN_APP_SQY_TWITTER".ljust(_space_)+"1\n"
    if "gmail"in applist.lower():
        appotherstr += "#define CVT_EN_APP_GOOGLE_ANDROID_GM".ljust(_space_)+"1\n"
    if "智象" in applist:
        appotherstr += "#define CVT_EN_APP_ZEASN_SK706".ljust(_space_)+"1\n"
    if "eshare" in applist.lower():
        appotherstr += "#define CVT_EN_APPLIST_ESHARE_SERVICE".ljust(_space_)+"1\n"
    if "miracast" in applist.lower():
        appotherstr += "#define CVT_EN_WFD".ljust(_space_)+"1\n"

    return appotherstr[:-1]

#--------------------------------------------------------
#  launcher
#  可以在modeID里面把launcher做好绑定，这边只定义一个宏即可
#--------------------------------------------------------
def createlauncher(launcher):
    if launcher == "公版免费":
        launcherstr = "#define CVT_DEF_LAUNCHER_TYPE".ljust(_space_)+"ID_LAUNCHER_40_NON_GAIA_SPACE"
    elif launcher == "公版GAIA":
        launcherstr = "#define CVT_DEF_LAUNCHER_TYPE".ljust(_space_)+"ID_LAUNCHER_40_GAIA_20_FALL"
    
    return launcherstr   


#--------------------------------------------------------
#  CEC
#--------------------------------------------------------
def createcec(cec):
    if "是" in cec:
        return "#define CVT_EN_CEC".ljust(_space_)+"1" + "\n" + "#define CVT_EN_ARC".ljust(_space_)+"1"
    else:
        return ""
        
#--------------------------------------------------------
#  ARC
#--------------------------------------------------------
def createarc(arc):
    if arc == "Yes":
        return "#define CVT_EN_ARC".ljust(_space_)+"1"
    elif arc == "No":
        return ""
        
#--------------------------------------------------------
#  hotel mode
#--------------------------------------------------------
def createhotel(hotelmode):
    if "是" in hotelmode:
        return "#define CVT_EN_HOTEL_MODE".ljust(_space_)+"1"
    else:
        return ""

#--------------------------------------------------------
#  CI
#--------------------------------------------------------
def createci(ci):
    if "+" in ci and "CI" in ci:
        return "#define CVT_DEF_CI_TYPE".ljust(_space_) + "ID_CI_TYPE_CI_PLUS"
    elif "CI" in ci or "是" in ci:
        return "#define CVT_DEF_CI_TYPE".ljust(_space_) + "ID_CI_TYPE_CI"
    else:
        return ""

#--------------------------------------------------------
#  power mode
#--------------------------------------------------------
def createpowermode(powermode):
    if powermode == "上电待机":
        return "#define CVT_DEF_POWERON_MODE".ljust(_space_)+"ID_POWERON_MODE_OFF"
    elif powermode == "记忆开机":
        return "#define CVT_DEF_POWERON_MODE".ljust(_space_)+"ID_POWERON_MODE_LAST"
    elif powermode == "上电开机":
        return "#define CVT_DEF_POWERON_MODE".ljust(_space_)+"POWERON_MODE_ON"

#--------------------------------------------------------
#  特殊需求编号索引
#  可以在代码里将特殊需求配置好，然后这边直接调用编号
#  也可以在这边根据编号来配置宏。
#--------------------------------------------------------

def  createspecialnum(specialnum):
    switcher = {
        "35x_001": (""),
    }
    return switcher.get(specialnum,"SPECIALNUM_ERROR")
