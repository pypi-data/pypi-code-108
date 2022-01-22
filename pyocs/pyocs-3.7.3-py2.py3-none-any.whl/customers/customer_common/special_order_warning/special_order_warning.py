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
faenamexls_name="特殊规则OCS过滤器维护表.xls"
home_dir = os.environ['HOME']
workspace = home_dir + '/'
workfilepath=workspace+faenamexls_name
order_list = list()


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
    print(workfilepath)
    work_book = xlrd.open_workbook(workfilepath)
    work_sheet = work_book.sheet_by_name('NameTab')

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
        return nameCon[ch_name],nameManager[ch_name];
    else:
        return "NO_THIS_NAME"


def get_warning_ocslink_from_drive_xls():
    print(workfilepath)
    work_book = xlrd.open_workbook(workfilepath)
    work_sheet = work_book.sheet_by_name('OCSWarning')

    # 'chinese_name'所在列为1，'pinyin_name'所在列为2，'manager_name'所在列为3；
    # 为了缩小代码量，此处直接使用硬编码
    for row in range(1, work_sheet.nrows):
        #print(str(work_sheet.cell_value(row, 1)))
        warning_customer = str(work_sheet.cell_value(row, 0))
        warning_ocslink = str(work_sheet.cell_value(row, 1))
        warning_note = str(work_sheet.cell_value(row, 2))
        print(warning_customer,warning_ocslink,warning_note)
        global order_list
        order_list.clear()
        order_list = get_all_mac_order_list(warning_ocslink)
        print(order_list)
        for ocsnum in order_list:
            print(ocsnum)
            ocsnum = ocsnum.replace('\n','')
            ocs_request = pyocs_demand.PyocsDemand(ocsnum)
            sw_engineer = ocs_request.get_ocs_software_engineer()
            sw_engineer = sw_engineer.replace('\n','')
            print(sw_engineer)
            fae_name,manager_name = get_fae_name_from_drive_xls(sw_engineer)
            print(fae_name,manager_name)
            deal_warning_tips(warning_customer,warning_note,ocsnum,fae_name,manager_name)

#获取所有需要预警的订单号list
def get_all_mac_order_list(warning_ocslink):

    p = PyocsRequest()
    r = p.pyocs_request_get(warning_ocslink)
    html = etree.HTML(r.text)
    original_ocs_list = html.xpath('//td[@class="Task_col_id"]')
    original_ocs_update_time_list = html.xpath('//td[@class="Task_col_update_time"]')
    for i in range(len(original_ocs_list)):
        order_list.append(original_ocs_list[i].text)

    return order_list



#处理预警信息
def deal_warning_tips(warning_customer,warning_note,ocsnum,fae_name,manager_name):
    msg = "【特殊规则风险订单提醒】【"+warning_customer+"】"+warning_note+"OCS号:"+ocsnum
    print(msg)
    tempStr='python "'+send_msg_py_path+'" "8a53fd1ac604" "'+msgType+'" "'+manager_name+'" "'+msg+'"'
    os.system(tempStr)
    #tempStr='python "'+send_msg_py_path+'" "8a53fd1ac604" "'+msgType+'" "'+manager_name+'" "'+msg+'"'
    #os.system(tempStr)

if __name__ == '__main__':
    _logger = logging.getLogger(__name__)
    download_file_form_drive()
    get_warning_ocslink_from_drive_xls()

