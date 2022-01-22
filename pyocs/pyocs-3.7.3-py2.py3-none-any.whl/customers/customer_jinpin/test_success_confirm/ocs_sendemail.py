#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib
import time
from pyocs import pyocs_login
from customers.customer_jinpin.test_success_confirm import checkout_engineer
import logging

class my_osc_sendemail:
    logger = logging.getLogger(__name__)
    def __init__(self):
        self.logger.setLevel(level=logging.WARNING)  # 控制打印级别

    account = pyocs_login.PyocsLogin().get_account_from_json_file()
    from_addr = str(account['Username']) + "@cvte.com"
    password = account['Password']
    smtp_server = 'smtp.exmail.qq.com'

    def _format_addr(slef,s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def get_engineer_name(fangan):
        get_engineer_in_charge = checkout_engineer.get_engineer()
        name=get_engineer_in_charge.check_engineer_name(fangan)
        return name

    def send_email_to_engineer(slef,toengineer,text_str):
        #msg = MIMEMultipart('alternative')
        #msgTEXT1 = MIMEText(text_str, 'plain', 'utf-8')#text_str发送正文，固定语句+确认不通过的订单信息
        #msgTEXT2 = MIMEText(TEXT2, 'plain', 'utf-8')
        #msg.attach(msgTEXT1)
        #msg.attach(msgTEXT2)
        msg = MIMEText(text_str, 'plain', 'utf-8')  # text_str发送正文，固定语句+确认不通过的订单信息
        msg['From'] =slef._format_addr('CVTE_林祥纳<%s>' % slef.from_addr)
        msg['To'] = ';'.join(toengineer)#以逗号形式连接起来 #_format_addr('管理员 <%s>' % to_addr)#可以采用把列表分开来的方法，一个一个发

        unpassed_str="脚本自动确认不通过的订单提醒"
        sys_time=time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
        subject_str=unpassed_str+sys_time
        msg['Subject'] = Header(subject_str, 'utf-8').encode()#subject_str发送主题内容
        #主题格式，时间+“确认不通过的订单提醒”

        server = smtplib.SMTP(slef.smtp_server, 25)
        server.set_debuglevel(1)
        server.login(slef.from_addr, slef.password)
        server.sendmail(slef.from_addr, toengineer, msg.as_string())
        server.quit()

    def failed_list_to_str(slef,fail_list):
        length=len(fail_list)
        get_str=''
        final_str = ''
        for i in range(0,length):
            if(fail_list[i][0]==None):
                fail_list[i][0]="                None"
            get_str="            ".join(fail_list[i])
            #tmp=get_str
            final_str=final_str+get_str+"\n"
        return final_str
