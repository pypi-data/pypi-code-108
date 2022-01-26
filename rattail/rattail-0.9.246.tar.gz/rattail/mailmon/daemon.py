# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Mail Monitor Daemon
"""

from __future__ import unicode_literals, absolute_import

import re
import time
import imaplib
# import sys
import logging
# from traceback import format_exception

import six

from rattail.daemon import Daemon
from rattail.db import api
from rattail.mailmon.config import load_mailmon_profiles
from rattail.mailmon.util import (get_lastrun,
                                  get_lastrun_setting,
                                  get_lastrun_timefmt)
from rattail.threads import Thread
from rattail.time import make_utc
from rattail.exceptions import StopProcessing
# from rattail.mail import send_email


log = logging.getLogger(__name__)


class MailMonitorDaemon(Daemon):
    """
    Daemon responsible for checking IMAP folders and detecting email
    messages, and then invoking actions upon them.
    """

    def run(self):
        """
        Starts watcher and worker threads according to configuration.
        """
        monitored = load_mailmon_profiles(self.config)

        # loop thru all accounts
        for key, account in six.iteritems(monitored['__accounts__']):

            # fire up the account watcher thread
            watcher = IMAPAccountWatcher(self.config, account)
            name = 'account_watcher_{}'.format(key)
            log.info("starting IMAP account watcher thread: %s", name)
            thread = Thread(target=watcher, name=name)
            thread.daemon = True
            thread.start()

        # loop indefinitely.  since this is the main thread, the app
        # will terminate when this method ends; all other threads are
        # "subservient" to this one.
        while True:
            time.sleep(.01)


class IMAPAccountWatcher(object):
    """
    Abstraction to make watching an IMAP account a little more
    organized.

    Instances of this class are used as callable targets when the
    daemon starts watcher threads.  The instance then is responsible
    for polling the IMAP folder(s) according to the monitor profiles
    associated with the account.
    """

    def __init__(self, config, account):
        self.config = config
        self.account = account
        self.server = None
        self.server_recycled = None
        self.app = config.get_app()
        self.lastrun_timefmt = get_lastrun_timefmt(self.config)

        # assume all profiles should be monitored at first
        for profile in self.account.monitored:
            profile.monitor = True

    def __call__(self):
        """
        This is the main loop for the account watcher.  It acts as the
        callable target for the thread in which it runs.  It basically
        checks for new messages, processing any found, then waits for
        a spell, then does it again, forever.
        """
        lastruns = {}
        last_error = None
        while True:

            # nb. each profile represents one folder
            for profile in self.account.monitored:

                # we may have stopped monitoring some profiles
                if not profile.monitor:
                    continue

                # track down last run time for this monitor profile
                # (nb. run times are maintained as zone-aware UTC)
                if profile.key in lastruns:
                    lastrun = lastruns[profile.key]
                else:
                    lastrun = get_lastrun(self.config, profile.key)
                    lastruns[profile.key] = lastrun

                # check if we should process this one again yet
                now = self.app.make_utc(tzinfo=True)
                if not lastrun or (now - lastrun).seconds >= profile.imap_delay:

                    # yep, so (try to) process
                    try:
                        self.process_profile(profile)

                    except:
                        log.exception("failed to process profile: %s", profile.key)

                        # presumably the error has to do with our server
                        # connection, so make sure we re-connect next time
                        self.disconnect()

                        # maybe stop monitoring this profile
                        if profile.stop_on_error:
                            profile.monitor = False

                        # skip the rest of this loop; let error delay
                        # handling kick in below
                        last_error = now
                        break

                    else:
                        # poll went okay, so record last run time
                        setting = get_lastrun_setting(self.config, profile.key)
                        api.save_setting(None, setting,
                                         now.strftime(self.lastrun_timefmt))
                        lastruns[profile.key] = now

            # maybe pause for a tick on account of error
            if last_error:
                if self.account.error_delay:
                    time.sleep(self.account.error_delay)
                last_error = None

            # and a general pause just to play nice
            time.sleep(0.01)

    def connect(self):

        # do we already have a connection?
        if self.server:

            # keep using forever if no recycle delay
            if not self.account.recycle_delay:
                return

            # okay so does it need to be recycled?
            now = self.app.make_utc()
            if (now - self.server_recycled).seconds < self.account.recycle_delay:

                # nope it's new enough to keep using
                return

            # too old, should recycle
            log.debug("recycle time limit reached (%s seconds), "
                      "disposing of current connection",
                      self.account.recycle_delay)
            self.disconnect()

        # establish new connection
        self.server = imaplib.IMAP4_SSL(self.account.server)
        result = self.server.login(self.account.username, self.account.password)
        log.debug("IMAP server login result: %s", result)
        self.server_recycled = self.app.make_utc()

    def disconnect(self):
        if not self.server:
            return

        try:
            self.server.close()
        except:
            log.exception("server.close() failed!")
        else:
            try:
                self.server.logout()
            except:
                log.exception("server.logout() failed!")
        finally:
            self.server = None

    def process_profile(self, profile, unread_only=None):
        """
        Poll a particular IMAP folder and process any messages found.
        """
        self.connect()

        # select the folder
        result = self.server.select(profile.imap_folder)
        log.debug("IMAP server select (%s) result: %s",
                  profile.imap_folder, result)

        # maybe look for "all" or maybe just "unread"
        if unread_only is None:
            unread_only = profile.imap_unread_only
        criterion = '(UNSEEN)' if unread_only else 'ALL'
        # log.debug("invoking IMAP4.search()")
        code, items = self.server.uid('search', None, criterion)
        if code != 'OK':
            raise RuntimeError("IMAP4.search() returned bad code: {}".format(code))

        # config may dictacte a "max batch size" in which case we will
        # only process so many messages at a time
        uids = items[0].split()
        if profile.max_batch_size:
            if len(uids) > profile.max_batch_size:
                uids = uids[:profile.max_batch_size]

        # process messages
        for uid in uids:
            self.perform_actions(profile, uid)

    def perform_actions(self, profile, msguid):
        """
        Perform all configured actions for the given message uid.
        """
        # ignore if we've stopped monitoring for this profile
        if not profile.monitor:
            return

        # log.debug("queue contained a msguid: %s", msguid)
        for action in profile.actions:
            try:
                self.invoke_action(action, msguid)

            except:
                # stop processing messages altogether for this
                # profile if it is so configured
                if profile.stop_on_error:
                    log.warning("an error was encountered, and config "
                                "dictates that no more actions should be "
                                "processed for profile: %s", profile.key)
                    profile.monitor = False
                    return

                # either way no more actions should be invoked for
                # this particular message
                break

    def invoke_action(self, action, msguid):
        """
        Invoke a single action on a mail message, retrying as necessary.
        """
        attempts = 0
        errtype = None
        while True:
            attempts += 1
            log.debug("invoking action '%s' (attempt #%s of %s) on file: %s",
                      action.spec, attempts, action.retry_attempts, msguid)

            try:
                action.action(self.server, msguid, *action.args, **action.kwargs)

            except:

                # if we've reached our final attempt, stop retrying
                if attempts >= action.retry_attempts:
                    # log.debug("attempt #%s failed for action '%s' (giving up) on "
                    #           "msguid: %s", attempts, action.spec, msguid,
                    #           exc_info=True)
                    log.exception("attempt #%s failed for action '%s' (giving up) on "
                              "msguid: %s", attempts, action.spec, msguid)
                    # TODO: add email support
                    # exc_type, exc, traceback = sys.exc_info()
                    # send_email(self.config, 'mailmon_action_error', {
                    #     # 'hostname': socket.gethostname(),
                    #     # 'path': path,
                    #     'msguid': msguid,
                    #     'action': action,
                    #     'attempts': attempts,
                    #     'error': exc,
                    #     'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
                    # })
                    raise

                # if this exception is not the first, and is of a
                # different type than seen previously, do *not* continue
                # to retry
                if errtype is not None and not isinstance(error, errtype):
                    log.exception("new exception differs from previous one(s), "
                                  "giving up on action '%s' for msguid: %s",
                                  action.spec, msguid)
                    raise

                # record the type of exception seen, and pause for next retry
                log.warning("attempt #%s failed for action '%s' on msguid: %s",
                            attempts, action.spec, msguid, exc_info=True)
                errtype = type(error)
                log.debug("pausing for %s seconds before making attempt #%s of %s",
                          action.retry_delay, attempts + 1, action.retry_attempts)
                if action.retry_delay:
                    time.sleep(action.retry_delay)

            else:
                # no error, invocation successful
                log.debug("attempt #%s succeeded for action '%s' on msguid: %s",
                          attempts, action.spec, msguid)
                break
