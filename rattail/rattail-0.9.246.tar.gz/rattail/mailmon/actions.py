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
Mail Monitor Actions
"""

from __future__ import unicode_literals, absolute_import

import os
import shutil
import tempfile

from rattail.monitoring import MonitorAction
from rattail.config import parse_bool
from rattail.files import locking_copy


class MessageAction(MonitorAction):
    """
    Base class for mailmon message actions.
    """

    def __call__(self, server, msguid, *args, **kwargs):
        """
        This method must be implemented in the subclass; it defines
        what the action actually *does*.  The monitor daemon will
        invoke this method for all new messages which are discovered.

        :param server: Reference to the ``imaplib.server`` instance,
           which will be connected with an active session.

        :param msguid: UID for the message upon which to act.
        """
        raise NotImplementedError


def download_message(server, msg_uid, output_dir, locking=False):
    """
    Simple action to "download" a message to local filesystem.

    :param output_dir: Path to the folder into which message should be
       written.  Note that the filename will be like
       ``{msg_uid}.eml``.

    :param locking: Flag to indicate that the
       :func:`rattail.files.locking_copy()` function should be used to
       place the file in its final location.  This is useful if you
       then also have a rattail filemon watching the ``output_dir``.
    """
    if not isinstance(locking, bool):
        locking = parse_bool(locking)

    # fetch message data
    code, msg_data = server.uid('fetch', msg_uid, '(RFC822)')
    if code != 'OK':
        raise RuntimeError("IMAP4.fetch() for msg_uid %s returned "
                           "bad code %s - msg_data is: %s",
                           msg_uid, code, msg_data)

    # extract message body
    response, msg_body = msg_data[0]

    # figure out where we need to write the file
    filename = '{}.eml'.format(msg_uid)
    if locking:
        tempdir = tempfile.mkdtemp()
        path = os.path.join(tempdir, filename)
    else: # no locking, write directly to file
        path = os.path.join(output_dir, filename)

    # write message to file
    with open(path, 'wb') as f:
        f.write(msg_body)

    # maybe move temp file to final path
    if locking:
        locking_copy(path, output_dir)
        shutil.rmtree(tempdir)
    

def move_message(server, msguid, newfolder):
    """
    Simple action to "move" a message to another IMAP folder, on the
    same server.
    """
    # copy msg to new folder
    code, response = server.uid('COPY', msguid, newfolder)
    if code != 'OK':
        raise RuntimeError("IMAP.copy(uid={}) returned bad code: {}".format(
            msguid, code))

    # mark old msg as deleted
    code, response = server.uid('STORE', msguid, '+FLAGS', '(\Deleted)')
    if code != 'OK':
        raise RuntimeError("IMAP.store(uid={}) returned bad code: {}".format(
            msguid, code))

    # expunge deleted messages
    code, response = server.expunge()
    if code != 'OK':
        raise RuntimeError("IMAP.expunge() returned bad code: {}".format(code))
