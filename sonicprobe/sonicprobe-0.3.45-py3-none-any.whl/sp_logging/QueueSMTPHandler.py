# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.sp_logging.QueueSMTPHandler"""

import smtplib

try:
    from email.utils import formatdate
except ImportError:
    from email.Utils import formatdate

from logging.handlers import SMTPHandler

from six import itervalues


class QueueSMTPHandler(SMTPHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject, logger_name = None):
        self.queue          = {}
        self.logger_name    = logger_name

        SMTPHandler.__init__(self, mailhost, fromaddr, toaddrs, subject)

    def isEmpty(self):
        return len(self.queue) == 0

    def getSubject(self, record):
        if self.logger_name:
            return "[%s] %s Event" % (self.logger_name, record.levelname)
        return "%s Event" % record.levelname

    def emit(self, record):
        if record.levelname not in self.queue:
            self.queue[record.levelname]    = []

        self.queue[record.levelname].append(record)

    def purge(self):
        if self.isEmpty():
            return

        queue       = dict(self.queue)
        self.queue  = {}

        for records in itervalues(queue):
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
                smtp = smtplib.SMTP(self.mailhost, port)
                msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" %
                       (self.fromaddr,
                        ','.join(self.toaddrs),
                        self.getSubject(record),
                        formatdate(),
                        msg))
                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            except Exception:
                self.handleError(record)
            finally:
                if smtp:
                    smtp.quit()
