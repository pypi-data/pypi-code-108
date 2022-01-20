import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Python 发送邮件

class EmailUtil(object):
    host = 'smtp.163.com'
    message = MIMEMultipart('related')
    email_client = smtplib.SMTP_SSL(host)

    def set_email_type(self, host, email_from, password):
        # host ='smtp.'+ email_from.split('@')[1]
        self.message['From'] = email_from
        self.email_client.connect(host, '465')
        self.email_client.login(email_from, password)

    def set_email_text(self, text):
        message = MIMEText(text, 'plain', 'utf-8')
        self.message.attach(message)

    def write_eamil_accessory(self, file_name, new_name):
        email_accessory = MIMEText(open(file_name, 'rb').read(), 'base64', 'utf-8')
        email_accessory.add_header("Content-Disposition", "attachment", filename=("utf-8", "", new_name))
        self.message.attach(email_accessory)

    def send_email(self, subject, receiver):
        self.message['Subject'] = subject
        if ',' in receiver:
            self.email_client.sendmail(from_addr=self.message['From'], to_addrs=receiver.split(','),
                                       msg=self.message.as_string())
        else:
            self.email_client.sendmail(from_addr=self.message['From'], to_addrs=receiver, msg=self.message.as_string())
            self.email_client.close()
