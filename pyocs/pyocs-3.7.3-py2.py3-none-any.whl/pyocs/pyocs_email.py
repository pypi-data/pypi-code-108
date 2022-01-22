import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header

password = 'Frank187029'


class PyocsEmail:

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别


    def send_email_with_cc(self, sender, receivers, cc, subject, content):

        print("启动邮件发送...")

        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header(sender)
        message['To'] = Header(receivers)
        message['Cc'] = Header(cc)
        # subject = '[OSM] 待发放订单自动维护详情报告'
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect('smtp.cvte.com')
            smtpObj.login(sender, password)  # 邮箱账号
            smtpObj.sendmail(sender, receivers.split(',') + cc.split(','), message.as_string())
            smtpObj.quit();
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")

    def send_email(self, sender, receivers, subject, content):

        print("启动邮件发送...")

        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header(sender)
        message['To'] = Header(receivers)
        # subject = '[OSM] 待发放订单自动维护详情报告'
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect('smtp.cvte.com')
            smtpObj.login(sender, password)  # 邮箱账号
            smtpObj.sendmail(sender, receivers, message.as_string())
            smtpObj.quit();
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
