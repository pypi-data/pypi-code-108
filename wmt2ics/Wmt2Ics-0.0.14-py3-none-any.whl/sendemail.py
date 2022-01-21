from wmt2ics.configemail import ConfigEmail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib


class SendEmail:
    '''Used to send an email with the attached file, great to
    use if you only have a computer and an iphone, like me. Open
    in native iOS mail app, click on attachment and add to
    calendar'''
    def __init__(self, pay_period, outfile):
        self.pay_period = pay_period
        self.outfile = outfile
        self.cfg = ConfigEmail().get_config()

    def send_mail(self):
        print("Attching " + self.outfile.split('/')[-1] + " to Email,\
         sending...")
        self.subject = "Pay Period " + self.pay_period + " File!"
        self.msg = MIMEMultipart()
        self.msg['From'] = "Web Scheduler to ICS"
        self.msg['TO'] = self.cfg["RECEIVER"]
        self.msg['Subject'] = self.subject
        self.body = "Remember to schedule yourself a pleasant day!\n"
        self.msg.attach(MIMEText(self.body, 'plain'))
        self.attachment = open(self.outfile, 'rb')
        self.part = MIMEBase('application', 'octet-stream')
        self.part.set_payload((self.attachment).read())
        encoders.encode_base64(self.part)
        self.part.add_header('Content-Disposition', "attachment;\
            filename= pay_period_"+self.pay_period+".ics")
        self.msg.attach(self.part)
        self.text = self.msg.as_string()
        self.server = smtplib.SMTP(self.cfg["SMTPSERVER"],
                                   int(self.cfg["SMTPPORT"]))
        self.server.starttls()
        self.server.login(self.cfg["SENDER"], self.cfg["APP_PWD"])
        self.server.sendmail(self.cfg["SENDER"], self.cfg["RECEIVER"],
                             self.text)
        self.server.quit()
        print("Email Sent Successfully!")


if __name__ == '__main__':
    SendEmail()
