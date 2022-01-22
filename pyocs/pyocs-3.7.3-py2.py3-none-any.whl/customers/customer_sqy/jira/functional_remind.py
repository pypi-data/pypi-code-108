#!/usr/bin/python
#coding:utf-8

import os
import sys
PROJ_HOME_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(1,PROJ_HOME_PATH)

import xlrd
import logging
from pyocs import pyocs_confluence
from pyocs.pyocs_filesystem import PyocsFileSystem
from pyocs.pyocs_login import PyocsLogin
from pathlib import Path
import re
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
import openpyxl
from customers.customer_common.common_database import commonDataBase


def download_faenamexls_form_drive():
    #从坚果云下载FAE姓名表格
    if Path(workfilepath).exists() is True:
        os.remove(workfilepath)
    db = commonDataBase()
    map_list = db.get_osm_distribute_mapping_info_by_user(faenamexls_name)
    download_link = map_list[0]
    PyocsFileSystem.get_file_from_nut_driver(download_link, workspace)

def download_funremindxls_form_drive():
    #从坚果云下载功能元提醒表格
    if Path(funremindfilepath).exists() is True:
        os.remove(funremindfilepath)
    db = commonDataBase()
    map_list = db.get_osm_distribute_mapping_info_by_user(funremindxls_name)
    funremindxls_download_link = map_list[0]
    PyocsFileSystem.get_file_from_nut_driver(funremindxls_download_link, workspace)

def get_fae_name_from_drive_xls(ch_name):
    work_book = xlrd.open_workbook(workfilepath)
    work_sheet = work_book.sheet_by_name('NameTab')

    nameCon={}
    #nameManager={}
    # 'chinese_name'所在列为1，'pinyin_name'所在列为2，'manager_name'所在列为3；
    for row in range(1, work_sheet.nrows):
        #print(str(work_sheet.cell_value(row, 1)))
        chinese_name = str(work_sheet.cell_value(row, 1))
        pinyin_name = str(work_sheet.cell_value(row, 2))
        manager_name = str(work_sheet.cell_value(row, 3))
        nameCon[chinese_name] = pinyin_name
        #nameManager[chinese_name] = manager_name
    if ch_name in nameCon:
        return nameCon[ch_name]#,nameManager[ch_name];
    else:
        return "NO_THIS_NAME"

def import_excel(excel_tables):
    '''
    打开excel表格，将excel表格内容导入到tables_list列表中
    '''
    tables_list = []  #创建一个空列表，存储功能元文件的数据

    for rown in range(1,excel_tables.max_row):
        array = {'功能元名称':'','功能元链接':'','创建人':'','创建日期':'','审核人':'','审核结果':'','问题点':''}
        array['功能元名称'] = excel_tables['A'+str(rown)].value#excel_tables.cell_value(rown,0)
        array['功能元链接'] = excel_tables['B'+str(rown)].value#excel_tables.cell_value(rown,1)
        array['创建人'] = excel_tables['C'+str(rown)].value#excel_tables.cell_value(rown,2)
        array['创建日期'] = excel_tables['D'+str(rown)].value#excel_tables.cell_value(rown,3)
        array['审核人'] = excel_tables['E'+str(rown)].value#excel_tables.cell_value(rown,4)
        array['审核结果'] = excel_tables['F'+str(rown)].value#excel_tables.cell_value(rown,5)
        array['问题点'] = excel_tables['G'+str(rown)].value#excel_tables.cell_value(rown,6)
        tables_list.append(array)

    tables_list.pop(0) #删掉第一列的数据

    return tables_list

def get_function_remind_info():
    creator_info_dict.clear()
    auditor_info_dict.clear()
    empty_info_list.clear()

    work_book = xlrd.open_workbook(funremindfilepath)
    # work_sheet = work_book.sheet_by_name('功能元')
    wb=openpyxl.load_workbook(funremindfilepath)
    shts=wb.get_sheet_names()
    sht=wb.get_sheet_by_name(shts[0])

    function_remind_list = import_excel(sht)

    for i in range(len(function_remind_list)):
        creator_name = function_remind_list[i]['创建人'].strip()
        if (function_remind_list[i]['审核人'] is None):
            auditor_name = ''
        else:
            auditor_name = function_remind_list[i]['审核人'].strip()

        if (function_remind_list[i]['审核结果'] is None):
            check_result = ''
        else:
            check_result = function_remind_list[i]['审核结果'].strip()

        if (check_result == 'NG'):
            if creator_name in creator_info_dict.keys():#如果字典的key值存在
                creator_info_dict[creator_name] += '###'+function_remind_list[i]['功能元名称']+'|||'+function_remind_list[i]['功能元链接']+'|||'+function_remind_list[i]['审核人']
            else:#如果字典的key值不存在
                creator_info_dict[creator_name] = function_remind_list[i]['功能元名称']+'|||'+function_remind_list[i]['功能元链接']+'|||'+function_remind_list[i]['审核人']
        elif (check_result == '待审核'):
            if auditor_name in auditor_info_dict.keys():#如果字典的key值存在
                auditor_info_dict[auditor_name] += '###'+function_remind_list[i]['功能元名称']+'|||'+function_remind_list[i]['功能元链接']+'|||'+function_remind_list[i]['创建人']
            else:#如果字典的key值不存在
                auditor_info_dict[auditor_name] = function_remind_list[i]['功能元名称']+'|||'+function_remind_list[i]['功能元链接']+'|||'+function_remind_list[i]['创建人']
        elif ((check_result == '') or (auditor_name == '')):
            empty_info_list.append(function_remind_list[i]['功能元名称']+'|||'+function_remind_list[i]['功能元链接']+'|||'+function_remind_list[i]['创建人'])

def send_email_to_creator():
    #邮件主题
    mail_subject = '【功能元】【待更新】待更新的功能元'

    #发送邮件
    for key,value in creator_info_dict.items():
        #邮件内容
        mail_text = 'Dear '+key+'：\n    以下功能元请按照审核建议修改，修改完之后请联系对应的审核人或者卢成帆修改审核状态，谢谢！\n\n'
        mail_text += '    功能元填写请参考KB：https://kb.cvte.com/pages/viewpage.action?pageId=162120581 \n\n\n'

        function_info_list = value.split('###')

        for fil in function_info_list:
            mail_text += '功能元名称：'+fil.split('|||')[0]+'\n功能元链接：'+fil.split('|||')[1]+'\n审核人：'+fil.split('|||')[2]+'\n\n'

        message = MIMEText(mail_text, 'plain')
        #发件人
        message['From'] = Header(sender)
        #收件人
        creator_email_address = get_fae_name_from_drive_xls(key)+'@cvte.com'
        message['To'] =  Header(creator_email_address)
        #抄送人
        message['Cc'] =  Header(Cc)
        #主题
        Subject = mail_subject+'  '+time.strftime("%Y%m%d", time.localtime())
        message['Subject'] = Header(Subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect('smtp.cvte.com')
            smtpObj.login(sender, password) #邮箱账号
            smtpObj.sendmail(sender, creator_email_address.split(',')+Cc.split(','), message.as_string())
            smtpObj.quit();
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")

def send_email_to_auditor():
    #邮件主题
    mail_subject = '【功能元】【待审核】待审核的功能元'

    #发送邮件
    for key,value in auditor_info_dict.items():
        #邮件内容
        mail_text = 'Dear '+key+'：\n    以下功能元请审核，审核完之后请在Excel中修改对应的状态，谢谢！\n\n'
        mail_text += '    功能元审核要求请参考KB：https://kb.cvte.com/pages/viewpage.action?pageId=162120581 \n\n\n'

        auditor_info_list = value.split('###')

        for fil in auditor_info_list:
            mail_text += '创建人：'+fil.split('|||')[2]+'\n功能元名称：'+fil.split('|||')[0]+'\n功能元链接：'+fil.split('|||')[1]+'\n\n'

        message = MIMEText(mail_text, 'plain')
        #发件人
        message['From'] = Header(sender)
        #收件人
        auditor_email_address = get_fae_name_from_drive_xls(key)+'@cvte.com'
        message['To'] =  Header(auditor_email_address)
        #抄送人
        message['Cc'] =  Header(Cc)
        #主题
        Subject = mail_subject+'  '+time.strftime("%Y%m%d", time.localtime())
        message['Subject'] = Header(Subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect('smtp.cvte.com')
            smtpObj.login(sender, password) #邮箱账号
            smtpObj.sendmail(sender, auditor_email_address.split(',')+Cc.split(','), message.as_string())
            smtpObj.quit();
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")

def send_email_to_administrator():
    #邮件主题
    mail_subject = '【功能元】【待确认】待确认状态的功能元'

    #发送邮件
    #邮件内容
    mail_text = 'Dear 卢成帆\n    以下功能元的状态为空，请及时处理，谢谢！\n\n\n'

    for fil in empty_info_list:
        mail_text += '创建人：'+fil.split('|||')[2]+'\n功能元名称：'+fil.split('|||')[0]+'\n功能元链接：'+fil.split('|||')[1]+'\n\n'

    message = MIMEText(mail_text, 'plain')
    #发件人
    message['From'] = Header(sender)
    #收件人
    message['To'] =  Header(luchengfan_email)
    #抄送人
    message['Cc'] =  Header(Cc)
    #主题
    Subject = mail_subject+'  '+time.strftime("%Y%m%d", time.localtime())
    message['Subject'] = Header(Subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.cvte.com')
        smtpObj.login(sender, password) #邮箱账号
        smtpObj.sendmail(sender,luchengfan_email, message.as_string())
        smtpObj.quit();
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

if __name__ == '__main__':
    #公共参数
    faenamexls_name="超7天未更新和超期jira提醒.xls"
    funremindxls_name="功能元.xlsx"
    home_dir = os.environ['HOME']
    workspace = './'#home_dir + '/pyocs/customers/customer_tcon/'
    workfilepath=workspace+faenamexls_name
    funremindfilepath=workspace+funremindxls_name

    #发件人
    sender = 'luchengfan@cvte.com'
    luchengfan_email = 'luchengfan@cvte.com'
    #抄送人
    Cc = 'luchengfan@cvte.com'
    #邮箱密码
    password  = PyocsLogin().get_account_from_json_file()["Password"]

    _logger = logging.getLogger(__name__)
    download_faenamexls_form_drive()
    download_funremindxls_form_drive()

    creator_info_dict = {} #审核结果为NG,发邮件给创建人
    auditor_info_dict = {} #审核结果为待审核,发邮件给审核人
    empty_info_list = [] #审核结果为空,发邮件给luchengfan

    get_function_remind_info()
    send_email_to_creator()
    send_email_to_auditor()
    if (len(empty_info_list) != 0):
        send_email_to_administrator()