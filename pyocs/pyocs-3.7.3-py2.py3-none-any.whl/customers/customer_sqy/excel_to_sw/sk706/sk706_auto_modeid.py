#!/usr/bin/env python3
import os
import string
import re
import sys

sys.path.append("/ssd2/zhanghonghai/codes/pyocs/pyocs")
sys.path.append("/ssd2/zhanghonghai/codes/pyocs/pyocs/customers/customer_sqy")
from pyocs import pyocs_demand
from excel_to_sw.PublicScripts.parse_excel import SoftwareRequest
from excel_to_sw.sk706.sk706_config_data import *
from create_intention_order import *


#===========================================================
##  根据指定排列规则生成MODEL ID
#===========================================================
def createmodeid(ocs_id,board,countryname,panel,ordernum):
    modeid = ocs_id.strip()+"_SQY_"+ordernum.strip() + "_" + board.strip() + "_" + countryname.strip()+"_"+panel.strip()
    modeid = modeid.replace(".", "_", 10)
    return modeid.replace("-", "_", 10)


#===========================================================
#  通过启悦订单号在OCS上检索是否存在相关订单，否则创建意向订单
#===========================================================
def get_ocs_id(ordernum):
    ocs_id = get_order_ocs_id(ordernum.replace("_","/"))
    
    #OCS上没有相关订单
    if ocs_id == 0:
        print("OCS 上没有查询到订单：" + ordernum.replace("_","/"))
        user_input = input("若需要创建意向订单，请输入 Y ：")
        if user_input == 'Y':
            intention_order_form_data_dict["data[Task][1][Task__subject]"] = customer_name + " " + bom_number
            ret = postHttpReqsToGetCustomerId(customer_name)
            ocs_id = create_intention_order()
            print("已新建如下意向订单：" + ocs_id)
        else:
            ocs_id = "CSXXXXXXX"

    else:
        ocs_title = pyocs_demand.PyocsDemand(ocs_id).get_ocs_title()
        print("OCS有现成的大货订单了，订单摘要:" + ocs_title)
        ocs_id = "CP" + ocs_id 
        
    return ocs_id


#========================================
#  输出红色字符
#========================================
def color_red_print(str):
    print("\033[1;31;40m%s\033[0m" % str)
    

#========================================
# 主程序
#========================================
def main():

    #从excel表格中获取数据
    sw_req = SoftwareRequest()

    ordernum   = str(sw_req.get_order_num()).strip()      #订单号
    bomnum     = str(sw_req.get_bom_num()).strip()        #客料号
    board      = str(sw_req.get_board_type()).strip()     #主版型号
    country    = str(sw_req.get_def_country()).strip()    #国家
    panel      = str(sw_req.get_panel_type()).strip()     #屏型号
    def_lang   = str(sw_req.get_def_language()).strip()   #默认语言
    lang_list  = str(sw_req.get_language_list()).strip()  #OSD语言
    ir         = str(sw_req.get_ir_type()).strip()        #遥控器
    keypad     = str(sw_req.get_keypad_type()).strip()    #按键板
    app_list   = str(sw_req.get_app_list()).strip()       #APP 
    # launcher   = str(sw_req.get_launcher())             #Launcher
    hotelmode  = str(sw_req.get_hotel_mode()).strip()     #酒店模式
    cec        = str(sw_req.get_cec_text()).strip()       #CEC
    ci         = str(sw_req.get_ci_type()).strip()        #CI
    specialnum = str(sw_req.get_special_needs())          #特殊需求

    print("\n[软件配置数据抓取如下]\n")
    print("ordernum: "  + ordernum)
    print("bomnum: "    + bomnum)
    print("board: "     + board)
    print("country: "   + country)
    print("panel: "     + panel)
    print("def_lang: "  + def_lang)
    print("lang_list: " + lang_list)
    print("ir: "        + ir)
    print("keypad: "    + keypad)
    print("app_list: "  + app_list)
    # print("launcher: "  + launcher)
    print("hotelmode: " + hotelmode)
    print("cec\\arc: "  + cec)
    print("ci: "  + ci)
    print("\n\n")

    countryname = switch_country_name(country)
    if "/" in panel:
        panel = panel.split("/")[1]
        panel = panel.replace(".","_")


    ocs_id = get_ocs_id(ordernum)
    modeid  = createmodeid(ocs_id,board,countryname,panel,ordernum)


    color_red_print("自动生成的MODEL ID配置如下：")
    print("#elif ( IsModelID( "+modeid+"))")

    color_red_print("//board")    
    print(createbom(bomnum))

    color_red_print("//ir keypad logo")
    print(createir(ir))
    print(createkeypad(keypad))

    color_red_print("//panel pq")
    print(createpanel(panel))

    color_red_print("//language")
    print(createdeflang(def_lang))
    print(createosdlanguage(lang_list))

    color_red_print("//country")
    print(createcountry(country))

    color_red_print("//APP")
    print(createappother(app_list))

    # color_red_print("//launcher")
    # print(createlauncher(launcher))

    color_red_print("//other")
    print(createcec(cec))
    print(createci(ci))
    print(createhotel(hotelmode))
    color_red_print("//END")



    # while(True):
    #     print("\n请仔细核对确认软件配置内容。按y/n")
    #     in_content = input("请输入：")
    #     if in_content == "y":
    #         print("自检ok")
    #         break
    #     elif in_content == "n":
    #         print("请修改后重新提交")
    #         exit()
    #     else:
    #         print("你输入的内容有误，请重输入！")

    #将配置的modeID写入customer_XXX.h
    # wirtemodefiedInCustomer(modeid,bomnum,panel,ir,logo,keypad,board,sound,def_lang,lang_list,country,appstore,miracast,appother,launcher,hotelmode,powermode,cec,arc,ttxnicam,specialnum)
    # print("成功写入customer.h")
    #下面是自动提交代码的逻辑
    # while(True):
    #     print("\n是否自动提交代码。按y/n")
    #     in_content = input("请输入：")
    #     if in_content == "y":
    #         autogitcommit(modeid)
    #         print("push完成")
    #         break
    #     elif in_content == "n":
    #         print("push终止")
    #         exit()
    #     else:
    #         print("你输入的内容有误，请重输入！")


    #下面是自动提交Jenkins的逻辑
    # while(True):
    #     print("\n是否自动提交Jenkins编译。按y/n")
    #     in_content = input("请输入：")
    #     if in_content == "y":
    #         os.system('pyocs jenkins '+modeid)
    #         print("####################")
    #         print("自动提交Jenkins成功")
    #         print("####################")
    #         break
    #     elif in_content == "n":
    #         print("Jenkins提交终止")
    #         exit()
    #     else:
    #         print("你输入的内容有误，请重输入！")

if __name__ == "__main__":
    main()

