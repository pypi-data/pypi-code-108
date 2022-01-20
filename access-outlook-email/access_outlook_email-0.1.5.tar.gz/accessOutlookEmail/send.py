"""
Created on 30.04.2021

@author: baier
"""

from exchangelib import Message, Mailbox, FileAttachment
from exchangelib.properties import HTMLBody


def send_email(account, subject, body, recipients, attachments=None):
    to_recipients = []
    for recipient in recipients:
        to_recipients.append(Mailbox(email_address=recipient))
    # Create message
    m = Message(account=account,
                folder=account.sent,
                subject=subject,
                body=HTMLBody(body),
                to_recipients=to_recipients)

    # attach files
    for attachment_name, attachment_content in attachments or []:
        file = FileAttachment(name=attachment_name, content=attachment_content)
        m.attach(file)

    m.send_and_save()
