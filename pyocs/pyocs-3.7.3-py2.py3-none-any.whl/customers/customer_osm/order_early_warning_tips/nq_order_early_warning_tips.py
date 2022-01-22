#!/usr/bin/python
#coding:utf-8
import os
import json
import requests
import xlrd
import logging
import urllib.parse
from lxml import etree
from pathlib import Path
from pyocs import pyocs_confluence
from pyocs.pyocs_filesystem import PyocsFileSystem
from pyocs import pyocs_login
from pyocs.pyocs_request import PyocsRequest
from pyocs import pyocs_demand
from customers.customer_common.common_database import commonDataBase


#公共数据区
msgType="SMS|WX"
send_msg_py_path="/disk2/zhaoxinan/pyocs/customers/customer_common/cvte_send_msg.py"
nq_order_early_warning_url="http://ocs-api.gz.cvte.cn/tv/TaskRelForecastWarms/index/page:1/tab:status_30/range:all"
faenamexls_name="工程师姓名部门维护表.xls"
home_dir = os.environ['HOME']
workspace = home_dir + '/'
workfilepath=workspace+faenamexls_name
waring_level_path='./nq_waring_level.txt'
ocs_list=[]
engineer_ocs_dict = {}

def download_file_form_drive():
    #从坚果云下载FAE姓名表格
    if Path(workfilepath).exists() is True:
        os.remove(workfilepath)
    db = commonDataBase()
    map_list = db.get_osm_distribute_mapping_info_by_user(faenamexls_name)
    download_link = map_list[0]
    print(download_link)
    PyocsFileSystem.get_file_from_nut_driver(download_link, workspace)

def get_fae_name_from_drive_xls(ch_name):
    work_book = xlrd.open_workbook(workfilepath)
    work_sheet = work_book.sheet_by_name('Sheet1')

    nameCon={}
    nameManager={}
    # 'chinese_name'所在列为1，'pinyin_name'所在列为2，'manager_name'所在列为3；
    # 为了缩小代码量，此处直接使用硬编码
    for row in range(1, work_sheet.nrows):
        #print(str(work_sheet.cell_value(row, 1)))
        chinese_name = str(work_sheet.cell_value(row, 1))
        pinyin_name = str(work_sheet.cell_value(row, 2))
        manager_name = str(work_sheet.cell_value(row, 3))
        nameCon[chinese_name] = pinyin_name
        nameManager[chinese_name] = manager_name
    if ch_name in nameCon:
        tempstr = nameCon[ch_name]
        return nameCon[ch_name];
    else:
        return "NO_THIS_NAME"


def get_pages_num():
    response = PyocsRequest().pyocs_request_get(nq_order_early_warning_url)
    html = etree.HTML(response.text)
    pages_xpath ='//p/text()'
    pages_str = html.xpath(pages_xpath)
    pagesstr_list = str(pages_str).split()
    for i in range (len(pagesstr_list)):
        if pagesstr_list[i] == "页面":
            temp_list = pagesstr_list[i+1].split('/')
            return int(temp_list[1])

#获取所有需要预警的订单号list
def get_all_early_warning_order_list():
    pagesnum = get_pages_num()
    print("一共有:"+str(pagesnum)+"页")


    #循环处理得到 OCS list
    for p in range(1,pagesnum+1):
        other_page_url = nq_order_early_warning_url.replace("page:1","page:"+str(p))
        print(other_page_url)
        pageresponse = PyocsRequest().pyocs_request_get(other_page_url)
        pagehtml = etree.HTML(pageresponse.text)
        original_ocs_list = pagehtml.xpath('//td[@class="TaskRelForecastWarm_task_id"]')
        inx = 0
        print(len(original_ocs_list))
        for inx in range(0,len(original_ocs_list)):
            ocs_list.append(original_ocs_list[inx].text)


#将姓名相同的不同ocs进行追加形成字典
def get_all_name_ocs_dict():
    print(len(ocs_list))
    for ocsnum in ocs_list:
        print(ocsnum)
        ocsnum = ocsnum.replace('\n','')
        ocs_request = pyocs_demand.PyocsDemand(ocsnum)
        title_msg = ocs_request.get_ocs_title()
        sw_ebs = ocs_request.get_ebs_num()
        sw_nq = ocs_request.get_nq()
        sw_nq = sw_nq.replace('\n','')
        print(sw_ebs)
        print(sw_nq)
        cvte_name = get_fae_name_from_drive_xls(sw_nq)
        print(cvte_name)

        #将姓名和ocs号追加形成字典
        if cvte_name in engineer_ocs_dict:
            if cvte_name == "NO_THIS_NAME":
                tempvalue = engineer_ocs_dict[cvte_name]+","+sw_nq
            else:
                tempvalue = engineer_ocs_dict[cvte_name]+","+str(sw_ebs)
            engineer_ocs_dict.update({""+cvte_name: ""+tempvalue})
        else:
            if cvte_name == "NO_THIS_NAME":
                engineer_ocs_dict.update({""+cvte_name: ""+sw_nq})
            else:
                engineer_ocs_dict.update({""+cvte_name: ""+str(sw_ebs)})

#处理预警信息
def deal_early_warning_tips(waring_level):
    print(engineer_ocs_dict)
    for key_name in engineer_ocs_dict:
        if key_name == "NO_THIS_NAME":
            msg = "【订单预警系统】 "+engineer_ocs_dict[key_name]+"需要在https://drive.cvte.com/p/DZhrHbkQsIgCGJ-kBw 中维护"
            tempStr='python "'+send_msg_py_path+'" "8a53fd1ac604" "'+msgType+'" "zhaoxinan" "'+msg+'"'
            os.system(tempStr)
        else:
            if waring_level == 1:
                msg = "【订单预警系统】 今日您有订单预警未处理,请在11点半前及时处理完毕，谢谢！EBS订单编号:"+engineer_ocs_dict[key_name]+" \
                \n请登录 https://ocs-api.gz.cvte.cn/tv/TaskRelForecastWarms/index/tab:status_30/range:my 处理!"
            elif waring_level == 2:
                msg = "【订单预警系统】 今日的预警处理不及时,会影响订单的正常发放,请立即处理，谢谢！EBS订单编号:"+engineer_ocs_dict[key_name]+" \
                \n请登录 https://ocs-api.gz.cvte.cn/tv/TaskRelForecastWarms/index/tab:status_30/range:my 处理!"            
            else:
                msg = "【订单预警系统】 今日您有订单预警需要及时处理,EBS订单编号:"+engineer_ocs_dict[key_name]+" \
                \n请登录 https://ocs-api.gz.cvte.cn/tv/TaskRelForecastWarms/index/tab:status_30/range:my 处理!"                
            
            print(msg)
            #tempStr='python "'+send_msg_py_path+'" "8a53fd1ac604" "'+msgType+'" "zhaoxinan" "'+msg+'"'
            #tempStr='python "'+send_msg_py_path+'" "8a53fd1ac604" "'+msgType+'" "'+key_name+'" "'+msg+'"'
            #os.system(tempStr)

if __name__ == '__main__':
    _logger = logging.getLogger(__name__)
    download_file_form_drive()
    get_all_early_warning_order_list()
    get_all_name_ocs_dict()

    if os.path.exists(waring_level_path):
        #记录文件存在
        fr = open(waring_level_path, 'r',encoding='utf-8',errors='ignore')
        old_level = fr.read()
        fr.close()
        new_level = 1
        fw = open(waring_level_path, 'w',encoding='utf-8',errors='ignore')
        if str(old_level) == "1":
            new_level = 2
        elif str(old_level) == "2":
            new_level = 1
        deal_early_warning_tips(new_level)
        fw.write(str(new_level))
        fw.close()
    else:
        #记录文件不存在
        #第一次运行,创建并写入文件
        f = open(waring_level_path, 'w',encoding='utf-8',errors='ignore')
        f.write("1")
        f.close()
        deal_early_warning_tips(1)
