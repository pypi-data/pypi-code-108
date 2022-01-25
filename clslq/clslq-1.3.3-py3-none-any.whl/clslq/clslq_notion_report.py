import datetime
import string
import os
# Support email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from openpyxl import Workbook
from openpyxl.styles import Border
from openpyxl.styles import Side

from clspy.log import Logger

from .templates import weekreport

clslog = Logger().log


class Report(object):
    """Base class of Report

    Args:
        object (wbname): Workbook name, generated document file name
    """
    def __init__(self, wbname):
        self.wb = Workbook()
        self.sht = self.wb.active
        self.default_border = Border(left=Side(border_style='thin',
                                               color='000000'),
                                     right=Side(border_style='thin',
                                                color='000000'),
                                     top=Side(border_style='thin',
                                              color='000000'),
                                     bottom=Side(border_style='thin',
                                                 color='000000'))
        self.wbname = wbname
        self.datetime_now = datetime.datetime.now()

    @property
    def now(self):
        return self.datetime_now

    def render_html_without_inline_css(self, title, df):
        """Render html form template, use pandas

        Note that some of the email display methods only support inline-css style,
        This method does not use any inline-css for table headers and rows.

        Deprecated

        Args:
            title (str): Title of html and email subject
            df (object): Pandas DataFrame object
        """
        clslog.info("Render html for {}".format(title))
        with open(self.wbname + '.html', encoding='utf-8', mode='w') as f:

            task = df[df[u'分类'] != u'工作计划']
            plan = df[df[u'分类'] == u'工作计划']

            t = string.Template(weekreport.wr_template)
            f.write(
                t.safe_substitute({
                    "title":
                    title,
                    "table":
                    task.to_html(classes='tablestyle', index=False, na_rep=""),
                    "plan":
                    plan.to_html(classes='tablestyle', index=False, na_rep="")
                }))

    def send_study_email(self, config, title, email_html):
        """Send report email to receivers defined in .clslq.json

        Args:
            config (dict): Loaded json object from .clslq.json
            title (str): Unicode string as email subject
        """
        email = config.get('email')
        smtpserver = email['sender']['smtpserver']
        user = email['sender']['user']
        pwd = email['sender']['pwd']
        receivers = email['study_receivers']
        clslog.info("{} {} {}".format(smtpserver, user, title))

        msg = MIMEMultipart()
        msg['From'] = "{}".format(user)
        msg['To'] = ",".join(receivers)
        msg['Subject'] = Header(title, 'utf-8')
        msg.attach(MIMEText(email_html, 'html', 'utf-8'))
        try:
            smtp = smtplib.SMTP()
            smtp.connect(smtpserver)
            smtp.login(user, pwd)
            smtp.sendmail(user, receivers, msg.as_string())
            clslog.info('Email sent to {} done'.format(receivers))
            smtp.quit()
            smtp.close()
        except Exception as e:
            clslog.critical("Exception @{}: {}".format(
                e.__traceback__.tb_lineno, e))

    def send_email(self, config, title):
        """Send report email to receivers defined in .clslq.json

        Args:
            config (dict): Loaded json object from .clslq.json
            title (str): Unicode string as email subject
        """
        email = config.get('email')
        smtpserver = email['sender']['smtpserver']
        user = email['sender']['user']
        pwd = email['sender']['pwd']
        receivers = email['receivers']
        clslog.info("{} {} {}".format(smtpserver, user, title))

        msg = MIMEMultipart()
        msg['From'] = "{}".format(user)
        msg['To'] = ",".join(receivers)
        msg['Subject'] = Header(title, 'utf-8')
        with open(self.wbname + '.html', "r", encoding='utf-8') as f:
            msg.attach(MIMEText(f.read(), 'html', 'utf-8'))
        try:
            smtp = smtplib.SMTP()
            smtp.connect(smtpserver)
            smtp.login(user, pwd)
            smtp.sendmail(user, receivers, msg.as_string())
            clslog.info('Email sent to {} done'.format(receivers))
            smtp.quit()
            smtp.close()
        except Exception as e:
            clslog.critical("Exception @{}: {}".format(
                e.__traceback__.tb_lineno, e))

    def remove_files(self):
        """Removes all generated files"""
        if os.path.exists(self.wbname + '.html'):
            os.remove(self.wbname + '.html')
        if os.path.exists(self.wbname + '.xlsx'):
            os.remove(self.wbname + '.xlsx')
