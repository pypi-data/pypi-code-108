#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Python SMTP发送邮件
import smtplib

from email.mime.text import MIMEText
from email.header import Header

mail_host = "mail.meituan.rolling_king"
mail_user = "zhengyu06@meituan.rolling_king"    #用户名
mail_pass = "Jason1qaz!QAZ"   #口令
sender = "zhengyu06@meituan.rolling_king"
receivers = ["386773780@qq.rolling_king"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

mail_msg = """
<p>Python 邮件发送测试...</p>
<p><a href="http://www.runoob.com">这是一个链接</a></p>
"""

message = MIMEText(mail_msg, 'html', 'utf-8')
message['From'] = Header("菜鸟教程", 'utf-8')
message['To'] = Header("测试", 'utf-8')

subject = 'Python SMTP 邮件测试'
message['Subject'] = Header(subject, 'utf-8')

try:
    print("连接邮件服务器...")
    smtpObj = smtplib.SMTP(mail_host, 25)
    print("连接邮件服务器成功。")
    # smtpObj = smtplib.SMTP()
    # smtpObj.connect(mail_host, 25)
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")

