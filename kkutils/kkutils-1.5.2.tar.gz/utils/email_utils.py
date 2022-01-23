#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Last modified: 2019-09-24 18:56:04
'''
import asyncio
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import aiosmtplib

__all__ = ['Email', 'AioEmail']


class EmailBase:

    def __init__(self, sender=None, smtp=None, user=None, pwd=None, use_tls=False):
        self.sender = sender or os.environ.get('EMAIL_SENDER')
        self.smtp = smtp or os.environ.get('EMAIL_SMTP')
        self.user = user or os.environ.get('EMAIL_USER')
        self.pwd = pwd or os.environ.get('EMAIL_PWD')
        self.use_tls = use_tls or os.environ.get('EMAIL_TLS')
        if isinstance(self.use_tls, str):
            self.use_tls = self.use_tls.lower() == 'true'

    def pack(self, receivers, title=None, content=None, files=None, cc=None):
        msg = MIMEMultipart()
        msg.set_charset('utf8')

        if content:
            mime = MIMEText(content, 'html', 'utf-8')
            msg.attach(mime)

        if files:
            if isinstance(files, (str, bytes)):
                files = [files]
            for i, fname in enumerate(files):
                '''
                _type, _ = mimetypes.guess_type(fname)
                if _type:
                    _type = _type.split('/')
                    att = MIMEBase(_type[0], _type[1], filename=fname)
                else:
                    att = MIMEBase('application', 'octet-stream')
                with open(fname, 'rb') as fp:
                    att.set_payload(fp.read())
                encoders.encode_base64(att)
                att['Content-ID'] = str(i)
                att["Content-Disposition"] = f'attachment; filename="{ os.path.basename(fname) }"'
                '''
                att = MIMEApplication(open(fname, 'rb').read())
                # att.add_header('X-Attachment-Id', str(i))
                att.add_header('Content-ID', str(i))
                att.add_header('Content-Type', 'application/octet-stream')
                att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(fname))
                msg.attach(att)

        if cc:
            if not isinstance(cc, list):
                cc = [cc]
            msg['cc'] = COMMASPACE.join(cc)

        msg['subject'] = title
        msg['date'] = formatdate(localtime=True)
        msg['from'] = self.sender
        if not isinstance(receivers, list):
            receivers = [receivers]
        msg['to'] = COMMASPACE.join(receivers)
        return msg


class Email(EmailBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.use_tls:
            self.client = smtplib.SMTP_SSL(self.smtp, 465)
        else:
            self.client = smtplib.SMTP(self.smtp)
        # self.client = smtplib.SMTP('localhost')
        # self.sender = self.client.local_hostname

    def send(self, *args, **kwargs):
        msg = self.pack(*args, **kwargs)
        self.client.docmd('ehlo', self.smtp)
        self.client.login(self.user, self.pwd)
        self.client.send_message(msg)
        self.client.quit()


class AioEmail(EmailBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs = {'port': 465, 'use_tls': True} if self.use_tls else {}
        self.client = aiosmtplib.SMTP(hostname=self.smtp, **kwargs)
        # self.client = smtplib.SMTP('localhost')
        # self.sender = self.client.hostname

    async def send(self, *args, **kwargs):
        msg = self.pack(*args, **kwargs)
        await self.client.connect()
        await self.client.login(self.user, self.pwd)
        await self.client.send_message(msg)
        await self.client.quit()


if __name__ == '__main__':
    email = AioEmail()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(email.send('429609918@qq.com', '你好', '世界'))
