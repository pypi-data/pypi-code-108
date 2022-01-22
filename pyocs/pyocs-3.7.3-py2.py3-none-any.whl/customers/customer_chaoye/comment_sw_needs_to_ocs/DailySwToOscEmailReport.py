#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import time
from email.header import Header
from email.mime.text import MIMEText
import datetime
import smtplib
from pyocs.pyocs_login import PyocsLogin

pyocs_login=PyocsLogin()
account_info = pyocs_login.get_account_from_json_file()
AutoDailylogpath = account_info["chaoye_request_autodeal_dailylog_path"]
#==============================================================
# 需要个人配置的地方
#==============================================================
#个人邮箱密码
password = 'xxxxxx'
#发件人
sender = 'zhaoxinan@cvte.com'
#收件人
receivers = 'liuyijun@cvte.com'+','+'yinze@cvte.com'+','+'likun@cvte.com'+','+'wudancheng@cvte.com'
#抄送人
Cc = 'aiwenpeng@cvte.com'+','+'zhaoxinan@cvte.com'

#==============================================================

#==============================================================
# 删除当天的日志文件
#==============================================================
def DeleteDailylog():
    if os.access(AutoDailylogpath, os.F_OK):
        os.remove(AutoDailylogpath)
    else:
        pass
#==============================================================
# 发送当天的日志文件
#==============================================================
def SendEmail():

    if os.access(AutoDailylogpath, os.F_OK):
        fp=open(AutoDailylogpath,"r")
        htmljira_texts=fp.read()
        fp.close()
    else:
        htmljira_texts = "当日无新增需求变更"


    message = MIMEText(htmljira_texts, 'text')
    #发件人
    message['From'] = Header(sender)
    #收件人
    message['To'] =  Header(receivers)
    #抄送人
    message['Cc'] =  Header(Cc)
    #主题
    Subject = '《朝野客户需求自动备注到OCS汇总日报》'+time.strftime("%Y%m%d", time.localtime())
    message['Subject'] = Header(Subject, 'utf-8')


    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.cvte.com')
        smtpObj.login(sender, password) #邮箱账号
        smtpObj.sendmail(sender, receivers.split(',')+Cc.split(','), message.as_string())
        smtpObj.quit();
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

if __name__ == '__main__':
    SendEmail()
    DeleteDailylog()

