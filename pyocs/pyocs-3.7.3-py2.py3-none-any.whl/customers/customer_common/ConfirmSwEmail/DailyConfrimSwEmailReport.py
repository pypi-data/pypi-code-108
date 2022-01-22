#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import time
from email.header import Header
from email.mime.text import MIMEText
import datetime
import smtplib
#==============================================================
# 需要个人配置的地方
#==============================================================
#个人邮箱密码
password = 'xxxxxx'
#发件人
sender = 'zhaoxinan@cvte.com'
#收件人
receivers = 'zhaoxinan@cvte.com'
#抄送人
Cc = 'zhaoxinan@cvte.com'+','+'zhaoxinan@cvte.com'

LogfileDailypath="/disk2/zhaoxinan/Toolszxn/Confirm_sw_email/pyocs/customers/customer_common/ConfirmSwEmail/LogfileDaily.txt"
Logfiletotalpath="/disk2/zhaoxinan/Toolszxn/Confirm_sw_email/pyocs/customers/customer_common/ConfirmSwEmail/Logfiletotal.txt"
#==============================================================
# 给总的文件增加时间戳
#==============================================================
def TotalfileWirteTime():
    ft = open(Logfiletotalpath, 'a+',encoding='utf-8',errors='ignore')
    timelog = "以上是"+time.strftime("%Y%m%d", time.localtime())+"确认邮件脚本自动处理情况\n"
    ft.write(timelog)
    ft.close()

#==============================================================
# 删除当天的日志文件
#==============================================================
def DeleteDailylog():
    if os.access(LogfileDailypath, os.F_OK):
        os.remove(LogfileDailypath)
    else:
        pass
#==============================================================
# 发送当天的日志文件
#==============================================================
def SendEmail():

    if os.access(LogfileDailypath, os.F_OK):
        fp=open(LogfileDailypath,"r")
        htmljira_texts=fp.read()
        fp.close()
    else:
        htmljira_texts = "当日无新增确认软件"


    message = MIMEText(htmljira_texts, 'text')
    #发件人
    message['From'] = Header(sender)
    #收件人
    message['To'] =  Header(receivers)
    #抄送人
    message['Cc'] =  Header(Cc)
    #主题
    Subject = '《客户确认邮件汇总日报》'+time.strftime("%Y%m%d", time.localtime())
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
    TotalfileWirteTime()
    SendEmail()
    DeleteDailylog()

