import os
import sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(1,BASE_PATH)
sys.path.insert(1,BASE_PATH + r"/customers/customer_jinpin")

from pyocs.pyocs_demand import PyocsDemand
from pyocs.pyocs_list import PyocsList
from pyocs.pyocs_software import PyocsSoftware
from pyocs.pyocs_request import PyocsRequest

import time
import datetime
import poplib
import smtplib
import telnetlib
import email
import email.policy
from email.parser import Parser
from email.header import Header
from email.header import decode_header
from email.utils import parseaddr
from email.mime.text import MIMEText

import json
import ast

import configparser
config = configparser.ConfigParser()
IniFilePath = "DRMOrderConf.ini"
config.read(IniFilePath)

def get_order_searchid(drm_summary_list):
    advanced_search = {
        "0":{
            "search_field_name":"Task.subject","search_field_id":"554","search_field_type":"5",
            "search_field_rel_obj":"null","search_opr":"TDD_OPER_INC",
            "input1":"金品","input2":'null',"offset":'null'},
        "1":{
            "search_field_name":"Task.status","search_field_id":"584","search_field_type":"19",
            "search_field_rel_obj":"Enums","search_opr":"TDD_OPER_INC",
            "input1":"待录入需求","input2":'null',"offset":'null'},
        "2":{
            "search_field_name":"Task.status","search_field_id":"584","search_field_type":"19",
            "search_field_rel_obj":"Enums","search_opr":"TDD_OPER_INC",
            "input1":"待上传软件","input2":'null',"offset":'null'},
        }

    i = 2
    for item in drm_summary_list:
        i = i + 1
        item_dict = {
            str(i):{"search_field_name":"Task.subject","search_field_id":"554","search_field_type":"5",
                "search_field_rel_obj":"null","search_opr":"TDD_OPER_INC",
                "input1":item,"input2":'null',"offset":'null'}
        }
        advanced_search.update(item_dict)

    condition_tmp = ''
    for index in range(4,i+2):
        if index == 4:
            condition_tmp = str(index)
        else:
            condition_tmp = condition_tmp + " or " + str(index)

    condition = "1 and (2 or 3) and (" + condition_tmp + ")"
    searchID = PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
    return searchID

def get_ocs_list_by_searchid(searchid):
    page = 1
    ocsList = []

    while True:
        searchidPara = str(searchid) + "/page:" + str(page)
        (count1tmp,list1tmp) = PyocsList().get_ocs_id_list(searchidPara)

        if count1tmp == 0:
            break

        ocsList = ocsList + list1tmp
        page = page + 1

    return ocsList

def print_to_file(something_need_to_print_to_file):
    # w+:打开一个文件用于读写。如果该文件已存在则打开文件，并从开头开始编辑，即原有内容会被删除。如果该文件不存在，创建新文件
    # a+:打开一个文件用于读写。如果该文件已存在，文件指针将会放在文件的结尾。文件打开时会是追加模式。如果该文件不存在，创建新文件用于读写。
    f = open("OCSProcessed.txt", 'w+')
    print(something_need_to_print_to_file, file=f)

def get_processed_ocs():
    f = open("OCSProcessed.txt", 'r')
    return f.read()

def get_drm_summary_list():
    return json.loads(config['drm']['summary'])

def send_email(ocs_list):
    mail_text = "以下订单客户需求带DRM，代测软件需要烧录Widevine KEY\n"
    for ocs in ocs_list:
        pd = PyocsDemand(ocs)
        engineer = pd.get_ocs_software_engineer()
        mail_text = mail_text + engineer + " http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:my/" + str(ocs) + "\n"

    sender = config['mail']['sender']
    receivers = config['mail']['receivers']
    passwaord = config['mail']['passwaord']

    message = MIMEText(mail_text, 'plain')
    #发件人
    message['From'] = sender
    #收件人
    message['To'] =  receivers
    #主题
    Subject = '《需求带DRM订单》' + time.strftime("%Y%m%d", time.localtime())
    message['Subject'] = Header(Subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.cvte.com')
        smtpObj.login(sender, passwaord) #邮箱账号
        smtpObj.sendmail(sender, receivers.split(','), message.as_string())
        smtpObj.quit();
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


if __name__ == '__main__':
    # processed_ocs = get_processed_ocs()
    # if processed_ocs == '':
    #     processed_ocs_list = []
    # else:
    #     processed_ocs_list = json.loads(processed_ocs.replace("'",'"'))

    ocs_list = get_ocs_list_by_searchid(get_order_searchid(get_drm_summary_list()))
    # print_to_file(ocs_list)

    # for processed_item in processed_ocs_list:
    #     if processed_item in ocs_list:
    #         ocs_list.remove(processed_item)
    if ocs_list:
        send_email(ocs_list)