from datetime import datetime

from nehushtan.mail.SMTPAgent import SMTPAgent
from tests.config import SMTP_CONFIG

now = datetime.now()

sm = SMTPAgent(
    sender=SMTP_CONFIG['sender'],
    password=SMTP_CONFIG['password'],
    smtp_server=SMTP_CONFIG['smtp_server'],
    smtp_port=SMTP_CONFIG['smtp_port']
) \
    .reset_receivers(['no-reply@anonymous.com']) \
    .set_subject('Test SMTP Agent') \
    .set_content(f'<h1>SMTP Agent</h1><p>It is a test mail</p><p>On {now}</p>') \
    .set_attachments(['test-for-smtp.py']) \
    .send()
