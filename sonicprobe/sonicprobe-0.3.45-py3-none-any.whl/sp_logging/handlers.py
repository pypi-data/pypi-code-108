# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.sp_logging.handlers"""

import smtplib

try:
    from email.utils import formatdate
except ImportError:
    from email.Utils import formatdate

from logging.handlers import SMTPHandler

from six import PY2, itervalues


class QueueSMTPHandler(SMTPHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials = None, secure = None, timeout = 5.0, logger_name = None):
        self.queues      = {}
        self.logger_name = logger_name
        self._timeout    = timeout

        if PY2:
            SMTPHandler.__init__(self, mailhost, fromaddr, toaddrs, subject, credentials, secure)
        else:
            SMTPHandler.__init__(self, mailhost, fromaddr, toaddrs, subject, credentials, secure, timeout)

    def isEmpty(self):
        return len(self.queues) == 0

    def getSubject(self, record):
        if self.logger_name:
            return "[%s] %s Event" % (self.logger_name, record.levelname)
        return "%s Event" % record.levelname

    def emit(self, record):
        if record.levelname not in self.queues:
            self.queues[record.levelname] = []

        self.queues[record.levelname].append(record)

    def purge(self):
        if self.isEmpty():
            return

        queues      = dict(self.queues)
        self.queues = {}

        for records in itervalues(queues):
            msg     = ""
            record  = None

            for record in records:
                msg += "%s\n" % self.format(record)

            if not record:
                continue

            smtp = None

            try:
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP(self.mailhost, port, timeout=self._timeout)
                msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" %
                       (self.fromaddr,
                        ",".join(self.toaddrs),
                        self.getSubject(record),
                        formatdate(),
                        msg))
                if self.username:
                    if self.secure is not None:
                        smtp.ehlo()
                        smtp.starttls(*self.secure)
                        smtp.ehlo()
                    smtp.login(self.username, self.password)
                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                self.handleError(record)
            finally:
                if smtp:
                    smtp.quit()
