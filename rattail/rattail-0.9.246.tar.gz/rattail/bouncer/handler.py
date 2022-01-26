# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Email Bounce Handlers
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import logging
import warnings
from email import message_from_string
from email.utils import parsedate_tz, mktime_tz

import six
from sqlalchemy import orm
from flufl.bounce import all_failures

from rattail.core import Object
from rattail.util import load_object


log = logging.getLogger(__name__)


def get_handler(config, key): # pragma: no cover
    """
    Return a bounce handler instance as specified by configuration.
    """
    warnings.warn("function is deprecated; please use "
                  "`app.get_bounce_handler() instead",
                  DeprecationWarning)
    app = config.get_app()
    return app.get_bounce_handler(key)


class Link(Object):
    """
    Simple representation of a link, to be shown in the Tailbone UI to assist
    with processing email bounces.
    """


class BounceHandler(object):
    """
    Default implementation for email bounce handlers.
    """

    def __init__(self, config, config_key):
        self.config = config
        self.config_key = config_key
        self.app = config.get_app()
        self.model = config.get_model()
        self.enum = config.get_enum()

    def get_all_failures(self, msg):
        warnings, failures = all_failures(msg)
        if warnings:
            warnings = ','.join(sorted(warnings))
        if failures:
            failures = ','.join(sorted(failures))
        return warnings, failures

    @property
    def root_msgdir(self):
        """
        The absolute path of the root folder in which messages are stored.
        """
        return os.path.abspath(self.config.require('rattail.bouncer', 'storage'))

    def msgdir(self, bounce):
        """
        Returns the absolute path of the folder in which the bounce's message
        file resides.  Note that the bounce must already have been persisted to
        the database.  The structure of the path returned is as follows:

        .. code-block:: none

           /{root_msgdir}/{uuid[:2]}/{uuid[2:]}

        * ``{root_msgdir}`` - Value returned by :meth:`root_msgdir()`.
        * ``{uuid[:2]}`` - First two characters of bounce UUID.
        * ``{uuid[2:]}`` - All UUID characters *after* the first two.

        .. note::
           While it is likely that the folder returned by this method already
           exists, this method does not guarantee any such thing.
        """
        return os.path.join(self.root_msgdir, bounce.uuid[:2], bounce.uuid[2:4], bounce.uuid[4:])

    def msgpath(self, bounce):
        return os.path.join(self.msgdir(bounce), 'bounce.eml')

    def handle_bounce_file(self, path, **kwargs):
        """
        Fully "handle" the given email message file, acting on it as
        needed, depending on whether or not it is actually considered
        to be a bounce etc.
        """
        with open(path, 'rt') as f:
            text = f.read()
        msg = message_from_string(text)

        warnings, failures = self.get_all_failures(msg)
        if failures:
            log.info("adding bounce for '%s': %s", path, failures)

            session = self.app.make_session()
            session.continuum_comment = "Received email bounce from {}".format(
                failures)

            bounce = self.make_bounce(msg, failures)
            session.add(bounce)
            session.flush()
            self.store_message_file(bounce, text)
            self.process_bounce(bounce)
            session.commit()

        elif warnings:
            log.warning("found message delivery warning for '%s': %s",
                        path, warnings)
        else:
            log.debug("found message with nothing interesting: %s", path)

    def make_bounce(self, msg, failures=None, **kwargs):
        model = self.model
        if failures is None:
            failed = self.get_failures(msg)
        kwargs.setdefault('config_key', self.config_key)
        kwargs.setdefault('bounced', self.get_bounced_time(msg))
        kwargs.setdefault('bounce_recipient_address', msg['To'])
        kwargs.setdefault('intended_recipient_address', failures)
        return model.EmailBounce(**kwargs)

    def process_bounce(self, bounce):
        pass

    def get_bounced_time(self, msg):
        date = parsedate_tz(msg['Date'])
        if date:
            return datetime.datetime.utcfromtimestamp(
                mktime_tz(date))
        return datetime.datetime.utcnow()

    def store_message_file(self, bounce, msg_body):
        msgdir = self.msgdir(bounce)
        os.makedirs(msgdir)
        path = os.path.join(msgdir, 'bounce.eml')
        with open(path, 'wb') as f:
            f.write(msg_body)
        return path

    def make_link(self, **kwargs):
        return Link(**kwargs)

    def make_links(self, session, recipient):
        model = self.model

        url = self.config.require('tailbone', 'url.customer')
        emails = session.query(model.CustomerEmailAddress).filter_by(address=recipient)
        for email in emails:
            yield self.make_link(type="Rattail Customer",
                                 title=six.text_type(email.customer),
                                 url=url.format(uuid=email.parent_uuid))

        url = self.config.require('tailbone', 'url.person')
        emails = session.query(model.PersonEmailAddress).filter_by(address=recipient)
        for email in emails:
            yield self.make_link(type="Rattail Person",
                                 title=six.text_type(email.person),
                                 url=url.format(uuid=email.parent_uuid))
