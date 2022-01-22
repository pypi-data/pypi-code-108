#import __init__
import os
import re
import time
import datetime

from pyocs import pyocs_excel

from pyocs import pyocs_software
from pyocs import pyocs_edit

from pyocs import pyocs_demand

from lxml import etree

import sys
import urllib

import os  # 导入模块

def download(url_str,save_path,filename):
    full_path = save_path + '/' + filename
    try:
        urllib.request.urlretrieve(url_str,full_path)
        return full_path
    except:
        return False

#issue for now 1,chinese code malform 2.xml not good some how

#step 1, get OCS number
ocsNum = input("please enter the OCS number: ")
#ocsNum = '652245'
print('ocsNum: '+ ocsNum)

#step 2, get customer_batch_code by ocsNum ex: 652245
OCSDEMAND = pyocs_demand.PyocsDemand(ocsNum)
customer_batch_code = OCSDEMAND.get_customer_batch_code()
print("customer_batch_code: "+customer_batch_code)

#step 3,download XML file to D:/ROKUOCS/origin.xml by ocsNum
ret = download('https://ocs-api.gz.cvte.cn/tv/Attachments/download_attachment/'+OCSDEMAND.get_xml_attach_id(),'D:/ROKUOCS','origin.xml')
print("download xml from OCS : "+ret)


#step 4,create new json file and prepare new xml test remark description base on customer_batch_code and D:/ROKUOCS/roku_infomation.xlsx
EX = pyocs_excel.PyocsExcel("D:/ROKUOCS/roku_infomation.xlsx", "A")
EX.set_customerCode_row(customer_batch_code)
jsonFileName = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')) +'_' + customer_batch_code +'_00001.cfg'
print("jsonFileName: "+jsonFileName)
print("making JSON file by D:/ROKUOCS/roku_infomation.xlsx and customer_batch_code is "+customer_batch_code)

testRemark = ""
jsonContent = ""
jsonContent += "{\n"

for i in range(EX.get_colNum_from_excel()):
    if(EX.get_keyByColIndex_from_excel(i)=="PID"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"ProjectID\": "+"\""+str(int(EX.get_valueByColIndex_from_excel(i)))+"\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"需求使用json文件在CVTE AT下烧录PID，先设置出厂 panel Pro_ID_" + str(int(EX.get_valueByColIndex_from_excel(i))) +" ，再做F1复位，具体参考测试指南5.4\" />"
    elif(EX.get_keyByColIndex_from_excel(i)=="SN"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"ODMSerial\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录SN条码：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "出厂设置"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and EX.get_valueByColIndex_from_excel(i) != ""):
            if (EX.get_valueByColIndex_from_excel(i) == "用户模式"):
                testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"最后需设置出货模式为长虹用户模式 ，具体操作方式参考测试指南5.9\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "品牌"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"Brand\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录品牌（Brand）：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "机型"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"OEMModel\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录TV型号（Oem model） ：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "USA服务器电话"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"SupportPhone\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录USA服务电话 ：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "USA服务器网址"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"SupportURL\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录USA服务器网址 ：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "CA服务器电话"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"SupportPhone\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录CA服务电话 ：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "CA服务器网址"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"SupportURL\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录CA服务器网址 ：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "MX服务器电话"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"SupportPhone\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录MX服务电话 ：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "MX服务器网址"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"SupportURL\": " + "\"" + EX.get_valueByColIndex_from_excel(i) + "\",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录MX服务器网址 ：" + EX.get_valueByColIndex_from_excel(i) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "生产日期"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"MfgDateYear\": "+ str(int(EX.get_valueByColIndex_from_excel(i)))[0:2] + ",\n"
            jsonContent += " \"MfgDateWeek\": "+ str(int(EX.get_valueByColIndex_from_excel(i)))[2:4] + ",\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"新增客制信息设置需求，需求使用json文件在CVTE AT下烧录生产日期（Manufacture Date）：" + str(int(EX.get_valueByColIndex_from_excel(i))) + "，具体操作方式参考测试指南\" />"
    elif (EX.get_keyByColIndex_from_excel(i) == "白平衡数据/Gamma数据"):
        if (EX.get_valueByColIndex_from_excel(i) != "无" and  EX.get_valueByColIndex_from_excel(i) != ""):
            jsonContent += " \"WBData\": [\n"
            wbnum = re.findall(r'\b\d+\b',EX.get_valueByColIndex_from_excel(i))

            jsonContent += "  " + str(wbnum[3])+",\n"
            jsonContent += "  " + str(wbnum[4]) + ",\n"
            jsonContent += "  " + str(wbnum[5]) + ",\n"

            jsonContent += "  " + "128" + ",\n"
            jsonContent += "  " + "128" + ",\n"
            jsonContent += "  " + "128" + ",\n"

            jsonContent += "  " + str(wbnum[0]) + ",\n"
            jsonContent += "  " + str(wbnum[1]) + ",\n"
            jsonContent += "  " + str(wbnum[2]) + ",\n"

            jsonContent += "  " + "128" + ",\n"
            jsonContent += "  " + "128" + ",\n"
            jsonContent += "  " + "128" + ",\n"

            jsonContent += "  " + str(wbnum[6]) + ",\n"
            jsonContent += "  " + str(wbnum[7]) + ",\n"
            jsonContent += "  " + str(wbnum[8]) + ",\n"

            jsonContent += "  " + "128" + ",\n"
            jsonContent += "  " + "128" + ",\n"
            jsonContent += "  " + "128" + "\n"

            jsonContent += " ],\n"
            testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\"需求使用json文件在CVTE AT下烧录白平衡数据 白平衡数据："+EX.get_valueByColIndex_from_excel(i)+"，具体操作方式参考测试指南\" />"


jsonContent = jsonContent[:-2] #just need to delete ths last douhao
jsonContent += "\n" # and add back \n
jsonContent += "}\n"
file_object = open('D:/ROKUOCS/'+jsonFileName, 'w')
file_object.write(jsonContent)
file_object.close()
print("done making json file : "+jsonFileName)

#step 5, upload the json file to a fix ocs page, and get the download link of the json file
OCSXML = pyocs_software.PyocsSoftware()
OCSXML.upload_software_to_ocs('652932','D:/ROKUOCS/'+jsonFileName,'D:/ROKUOCS/origin.xml','100','0','2','xx','True')
link = OCSXML.get_software_download_link('652932',jsonFileName)
link = 'json文件名：'+link.name+' 链接：'+link.download_link +' 有效截止时间：'+ link.deadline
testRemark += "<Attr Name=\"SW_FAC_TESTING_REMARK\" Alias=\"SW_FAC_TESTING_REMARK\" Ids=\"0\" Atoms=\""+link+" \" />"
print("done upload json file to a fix ocs page 652932")

#step 6, base on testremark we prepared before,we modify origin.xml test remak and make a new.xml
remarkComing = 0
needAddSwitemEnd = 0
f1 = open('D:/ROKUOCS/origin.xml','r',encoding='utf-8')    # 以“r”(只读)模式打开旧文件
f2 = open('D:/ROKUOCS/new.xml','w',encoding='utf-8')  # 以“w”(写)模式打开或创建新文件（写模式下，文件存在则重写文件，文件不存在则创建文件）
for lines in f1:
    if (("SW_FAC_TESTING_REMARK" in lines)):
        remarkComing = 1;
        if (("SW_Items" in lines)):
            needAddSwitemEnd = 1
    else:
        if ('<' not in lines):
            continue
        if (remarkComing == 1):
            remarkComing = 0
            if (needAddSwitemEnd == 1):
                testRemark += "</SW_Items>"
            testRemark += "\n"
            f2.write(testRemark)
        f2.write(lines)
f1.close()
f2.close()
print("done making new.xml, ready upload to "+ocsNum+" and refeash")

#step 7, upload new.xml to ocs

OCSED = pyocs_edit.PyocsEdit()
OCSED.update_ocs_xml(ocsNum,'D:/ROKUOCS/new.xml','all')
print("done upload new.xml,  to "+ocsNum+" and all task done")
print("恭喜你，所有任务都完成了")
os.system("pause")

