#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# 发送邮件

import os
import smtplib
import sys
import yaml
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from HTest import new_report, get_yaml
from HTest.logger import logger

sys.path.append(os.path.dirname(__file__))
EMAIL_DIR = os.path.join(get_yaml().get('BASE_DIR'), "config", "config.yaml")
TEST_REPORT = os.path.join(get_yaml().get('BASE_DIR'), "report")


def get_config(path):
    f = open(path, encoding='utf-8')
    data = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    return data


def send_email(file):
    # 邮件配置
    data = get_config(EMAIL_DIR).get("email", {})
    username_send = data['FROM']  # 发件人
    username_received = data['TO']  # 收件人可以是多人
    email_server = data['HOST_SERVER']   # 邮箱服务端url
    username_code = data['user_code']   # 邮箱授权码

    # 构造MIMEMultipart对象做为根容器
    email = MIMEMultipart()
    # 设置根容器属性
    email['Subject'] = data['SUBJECT']
    email['From'] = username_send
    email['To'] = ','.join(username_received)

    # 构造MIMEText对象做为邮件显示内容并附加到根容器
    text_msg = MIMEText("Hi All,\n \n   这是本次测试的测试报告，详情见附件。\n \nBest Wishes!")
    email.attach(text_msg)
    # 构造MIMEBase对象做为邮件附件内容并附加到根容器
    att = MIMEBase('application', 'octet-stream')
    att.set_payload(open(file, 'rb').read())
    att.add_header('Content-Disposition', 'attachment', filename=Header(file, 'gbk').encode())
    encoders.encode_base64(att)
    email.attach(att)

    # 发邮件
    try:
        smtp = smtplib.SMTP_SSL(email_server, port=465)
        smtp.login(email['From'], username_code)
        smtp.sendmail(email['From'], email['To'], email.as_string())
        logger.info("测试报告已发送成功")
        smtp.quit()
    except Exception as e:
        logger.error("邮件发送失败" + str(e))


if __name__ == '__main__':
    report = new_report(TEST_REPORT)
    send_email(report)
