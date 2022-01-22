import sys
sys.path.insert(1,"/ssd1/luchengfan/pyocs")
sys.path.insert(2,"/ssd1/luchengfan/pyocs/pyocs")

from pyocs.pyocs_software import PyocsSoftware
from pyocs.pyocs_login import PyocsLogin
from pyocs import pyocs_searchid
from pyocs import pyocs_demand

import re
import os
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

#发件人
sender = 'luchengfan@cvte.com'
#抄送人
Cc = 'luchengfan@cvte.com'
#邮箱密码
password   = PyocsLogin().get_account_from_json_file()["Password"]

def get_ocs_audit_person():
    dict_audit_order_ocs.clear()

    advanced_search = {
        "0":{"search_field_name":"Task.rd_dept_id",
             "search_field_id":"546",
            "search_field_type":"19",
            "search_field_rel_obj":"Depts",
            "search_opr":"TDD_OPER_INC",
            "input1":"TCON",
            "input2":'null',
            "offset":'null'},
        "1":{"search_field_name":"Task.status",
             "search_field_id":"584", 
             "search_field_type":"19",
             "search_field_rel_obj":"Enums",
             "search_opr":"TDD_OPER_EQUAL",
             "input1":"软件待审核",
             "input2":'null',
             "offset":'null'}
    }

    condition = "1 and 2"

    si = pyocs_searchid.PyocsSearchid((PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)))

    for i in si.get_ocs_id_list_info():
        ocs_request = pyocs_demand.PyocsDemand(i)
        ocs_order_auditor = ocs_request.get_software_audit()
        if ocs_order_auditor in dict_audit_order_ocs.keys():#如果字典的key值存在
            dict_audit_order_ocs[ocs_order_auditor] = dict_audit_order_ocs[ocs_order_auditor] + ',' + i
        else:#如果字典的key值不存在
            dict_audit_order_ocs[ocs_order_auditor] = i

def send_email():
    #邮件主题
    mail_subject = 'TCON待审核订单'

    #审核人员：邮箱
    dict_auditor = {'黄小华':'huangxiaohua@cvte.com' , '甘年平':'gannianping@cvte.com' , '卢成帆':'luchengfan@cvte.com'}

    #发送邮件
    for key,value in dict_audit_order_ocs.items():
        mail_text = ''
        if key in dict_auditor.keys():
            #邮件内容
            mail_text = 'Dear '+key+'：\n    以下为需要审核的TCON订单，请及时处理，谢谢！\n\n'
            ocs_list = value.split(',')

            for ocs_id in ocs_list:
                mail_text += '    http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:my/'+ ocs_id+'\n'

            message = MIMEText(mail_text, 'plain')
            #发件人
            message['From'] = Header(sender)
            #收件人
            message['To'] =  Header(dict_auditor[key])
            #抄送人
            message['Cc'] =  Header(Cc)
            #主题
            Subject = mail_subject+'  '+time.strftime("%Y%m%d", time.localtime())
            message['Subject'] = Header(Subject, 'utf-8')

            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect('smtp.cvte.com')
                smtpObj.login(sender, password) #邮箱账号
                smtpObj.sendmail(sender, dict_auditor[key].split(',')+Cc.split(','), message.as_string())
                smtpObj.quit();
                print("邮件发送成功")
            except smtplib.SMTPException:
                print("Error: 无法发送邮件")
        else:
            if (key != '无'):
                mail_text = 'TCON订单有新的审核人员，请及时处理。新的审核人员为：'+ key
                message = MIMEText(mail_text, 'plain')
                #发件人
                message['From'] = Header(sender)
                #收件人
                message['To'] =  Header(sender)
                #主题
                Subject = mail_subject+'  '+time.strftime("%Y%m%d", time.localtime())
                message['Subject'] = Header(Subject, 'utf-8')

                try:
                    smtpObj = smtplib.SMTP()
                    smtpObj.connect('smtp.cvte.com')
                    smtpObj.login(sender, password) #邮箱账号
                    smtpObj.sendmail(sender, sender, message.as_string())
                    smtpObj.quit();
                    print("邮件发送成功")
                except smtplib.SMTPException:
                    print("Error: 无法发送邮件")

if __name__ == '__main__':
    #审核人员：需要审核的OCS订单
    dict_audit_order_ocs = {}

    #获取订单审核人员
    get_ocs_audit_person()

    #发送对用邮件给对应人员
    send_email()

