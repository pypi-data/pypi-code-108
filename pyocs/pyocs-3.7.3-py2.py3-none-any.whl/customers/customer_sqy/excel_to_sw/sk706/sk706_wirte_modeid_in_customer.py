from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createbom
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createlogo
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createkeypad
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createpanel
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createir
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createdeflang
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createosdlanguage
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createcountry
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createsound
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createappstore
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createmiracast
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createappother
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createlauncher
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createhotel
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createcec
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createarc
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createpowermode
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import createspecialnum
from customers.customer_sqy.excel_to_sw.sk706.sk706_Config_Data import switch_country_name
#--------------------------------------------------------
#  wirte the modefied in customer_xxx.h
#  下面这个路劲可以改成你的对应方案的customer_xxx.h
#--------------------------------------------------------
customer_cy_508_path = "/hdd1/zhanghonghai/codes/Android/hisi/35x_fae_ap/customers/customer/customer_sqy/customer_sqy.h"

def wirtemodefiedInCustomer(modeid,bomnum,panel,ir,logo,keypad,board,sound,def_lang,osd_lang,country,appstore,miracast,appother,launcher,hotelmode,powermode,cec,arc,ttxnicam,specialnum):
    count= 0
    definelinenum = getFlagCurrentLine("//model_id_define_end")
    definelinenum = definelinenum - 1 #获取标志位的上一行行数

    modeidlinenum = getFlagCurrentLine("//model_id_content_end")
    modeidlinenum = modeidlinenum - 1 #获取标志位的上一行行数

    with open(customer_cy_508_path,"r") as f_cus:
        lines_old = f_cus.readlines()
    with open(customer_cy_508_path,"w") as f_cus:
        for line in lines_old:
            count += 1
            if count == definelinenum:
                line.split()
                modeidlist = line.split(' ')
                curmodeidnum = str(int(modeidlist[-1]) + 1)
            if "//model_id_define_end" in line:
                f_cus.write("#define "+modeid+'             '+curmodeidnum+'\n')
            if "#define MODEL_ID" in line:
                f_cus.write("#define MODEL_ID  "+modeid+'\n')
                continue
            if count == modeidlinenum:
                f_cus.write("#elif ( IsModelID("+modeid+"))\n")
                f_cus.write("//-------------------------------------- Board ----------------------------------------------\n")
                f_cus.write(createbom(bomnum))
                f_cus.write("//-------------------------------------- panel pq -------------------------------------------\n")
                f_cus.write(createpanel(panel))
                f_cus.write("//---------------------------------- ir keypad logo -----------------------------------------\n")
                f_cus.write(createir(ir))
                f_cus.write(createlogo(logo))
                f_cus.write(createkeypad(keypad))
                f_cus.write("//-------------------------------------- Sound ----------------------------------------------\n")
                f_cus.write(createsound(board, sound))
                f_cus.write("//-------------------------------------- Language -------------------------------------------\n")
                f_cus.write(createdeflang(def_lang))
                f_cus.write(createosdlanguage(osd_lang))
                f_cus.write("//-------------------------------------- country --------------------------------------------\n")
                f_cus.write(createcountry(country))
                f_cus.write("//-------------------------------------- APP ------------------------------------------------\n")
                f_cus.write(createappstore(appstore))
                f_cus.write(createmiracast(miracast))
                f_cus.write(createappother(appother))
                f_cus.write("//-------------------------------------- Launcher -------------------------------------------\n")
                f_cus.write(createlauncher(launcher))
                f_cus.write("//-------------------------------------- Other ----------------------------------------------\n")
                f_cus.write(createhotel(hotelmode))
                f_cus.write(createpowermode(powermode))
                f_cus.write(createcec(cec))
                f_cus.write(createarc(arc))
                f_cus.write(createttxnicam(ttxnicam))
                f_cus.write(createspecialnum(specialnum))
                f_cus.write("//END\n")

            f_cus.write(line)
        f_cus.close()


# 获得当前modeID的行数
def getFlagCurrentLine(flag):
    count = 0 #计行器
    currentline = 0 #当前modeID行数
    customerfile = open(customer_cy_508_path)
    for line in customerfile.readlines():
        count += 1
        if flag in line:
            currentline  = count
    return currentline
