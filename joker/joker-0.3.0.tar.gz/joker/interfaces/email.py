#!/usr/bin/env python3
# coding: utf-8

import logging
import mimetypes
import os.path
import smtplib
from email.message import EmailMessage
from typing import Union, List

_logger = logging.getLogger(__name__)


class ExtendedEmailMessage(EmailMessage):
    @staticmethod
    def _fmt_addrs(addrs: Union[List[str], str], sep=', '):
        if isinstance(addrs, str):
            return addrs
        return sep.join(addrs)

    def set_subject_and_addrs(
            self, subject: str, from_addr: str,
            to_addrs: Union[List[str], str],
            cc_addrs: Union[List[str], str] = None):
        self['Subject'] = subject
        self['From'] = from_addr
        self['To'] = self._fmt_addrs(to_addrs)
        if cc_addrs:
            self['Cc'] = self._fmt_addrs(cc_addrs)

    def add_attachment_from_local_file(self, path: str):
        mime = mimetypes.guess_type(path)[0]
        maintype, subtype = mime.split('/', 1)
        filename = os.path.split(path)[1]
        with open(path, 'rb') as fin:
            content = fin.read()
            self.add_attachment(
                content, filename=filename,
                maintype=maintype, subtype=subtype,
            )


class EmailInterface:
    def __init__(
            self, host: str, port: int,
            username: str, password: str,
            from_addr: str, fake=False):
        """
        Args:
            host:
            port:
            username:
            password:
            from_addr:
            fake: if true, messages will NOT be send actually
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.fake = fake

    def _get_smtp(self):
        smtp = smtplib.SMTP(self.host, self.port)
        smtp.login(self.username, self.password)
        return smtp

    def _send(self, from_addr, to_addrs, msg):
        smtp = self._get_smtp()
        try:
            resp = smtp.sendmail(from_addr, to_addrs, msg)
            _logger.info("smtp.sendmail() => %s", resp)
        finally:
            smtp.quit()
            _logger.info("smtp.quit()")
        return resp

    def send(
            self,
            subject: str,
            content: str,
            attachments: list,
            from_addr: Union[str, None],
            to_addrs: Union[List[str], str],
            cc_addrs: Union[List[str], str] = None,
            content_subtype='html'):
        """
        Args:
            subject:
            content:
            attachments
            from_addr: override default from_addr
            to_addrs:
            cc_addrs:
            content_subtype:
        """
        from_addr = from_addr or self.from_addr
        mail = ExtendedEmailMessage()
        mail.set_subject_and_addrs(
            subject, from_addr, to_addrs, cc_addrs,
        )
        mail.set_content(content, subtype=content_subtype)
        for att in attachments:
            mail.add_attachment_from_local_file(att)

        msg = mail.as_string()
        _logger.debug('EmailMessage().as_string()[:100] => %s', msg[:100])
        _logger.info('EmailMessage().fake => %s', self.fake)
        if not self.fake:
            return self._send(from_addr, to_addrs, msg)
