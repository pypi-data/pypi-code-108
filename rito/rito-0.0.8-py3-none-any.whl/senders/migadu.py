import os
from email.header import Header
import email
import json
import time
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import sys
import markdown

if 'RITO_MIGADU_ACCOUNT' not in os.environ or 'RITO_MIGADU_PASSWORD' not in os.environ:
    print("To use Rito's Migadu functions, you need to create a Migadu domain and create a bot mailbox on your domain with no privileges.")
    print("Put the bot account's credentials in the environment variables RITO_MIGADU_ACCOUNT and RITO_MIGADU_PASSWORD, then try again.")
    exit(1)

account = os.environ['RITO_MIGADU_ACCOUNT']
password = os.environ['RITO_MIGADU_PASSWORD']

def send_message(to_address, text):
    """ Function that the CLI will call if --migadu [addresses] is passed in. """
    #subject and body will be the same for messages via CLI.
    send_email_plain([to_address], text, text)

def send_email_plain(recipients, subject, body, files=[]):
    """ Send a plain utf8 email to the specified addresses """
    __send_email(recipients, subject, body, 'plain', files)

def send_email_markdown(recipients, subject, body_markdown, files=[]):
    """ Send a markdown-formatted email to the specified list of addresses
    """
    # Convert the markdown to HTML
    body_html = markdown.markdown(body_markdown)
    __send_email(recipients, subject, body_html, 'html', files)

def __with_smtp(func):
    with smtplib.SMTP_SSL("smtp.migadu.com", 465) as smtp:
        # Log in to the email account
        smtp.login(account, password)
        func(smtp)

def __send_email(recipients, subject, content, encoding, files=[]):
    # accept a single string in place of the recipients list, for ergonomic use:
    if type(recipients) is not list: recipients = [ recipients ]

    # Construct the message as a MIMEMultipart with MIMEText
    message = MIMEMultipart()
    message['From'] = account
    message['To'] = COMMASPACE.join(recipients)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = Header(subject.encode('utf-8'), 'utf-8')

    message.attach(MIMEText(content.encode('utf-8'), encoding, 'utf-8'))

    # source of attachment code: https://stackoverflow.com/a/3363254
    for f in files:
        if f != "":
            try:
                with open(f, 'rb') as ff:
                    part = MIMEApplication(
                        ff.read(),
                        Name=basename(f),
                    )
                # After the file is closed
                part['Content-Disposition'] = f'attachment; filename="{basename(f)}"'
                message.attach(part)
            except:
                raise f"Couldn't attach {f}."

    __with_smtp(lambda smtp : smtp.sendmail(account, recipients,message.as_string()))