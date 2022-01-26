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
Console Commands
"""

from __future__ import unicode_literals, absolute_import

import os
import sys
import time
import datetime
import socket
import logging

from rattail.commands import Subcommand
from rattail.time import make_utc, localtime


log = logging.getLogger(__name__)


class DataSync(Subcommand):
    """
    Manage the data sync daemon
    """
    name = 'datasync'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')

        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        check = subparsers.add_parser('check', help="(DEPRECATED) Check for stale (lingering) changes in queue")
        check.set_defaults(subcommand='check')

        check_queue = subparsers.add_parser('check-queue', help="Check for stale (lingering) changes in queue")
        check_queue.set_defaults(subcommand='check-queue')

        check_watchers = subparsers.add_parser('check-watchers', help="Check for dead watcher threads")
        check_watchers.set_defaults(subcommand='check-watchers')

        collectd = subparsers.add_parser('collectd', help="Output statistics for collectd")
        collectd.set_defaults(subcommand='collectd')

        wait = subparsers.add_parser('wait', help="Wait for changes to be processed")
        wait.set_defaults(subcommand='wait')

        remove_settings = subparsers.add_parser(
            'remove-settings',
            help="Remove all datasync settings from the DB")
        remove_settings.set_defaults(subcommand='remove-settings')

        parser.add_argument('-p', '--pidfile', metavar='PATH', default='/var/run/rattail/datasync.pid',
                            help="Path to PID file.")
        parser.add_argument('--daemonize', action='store_true',
                            help="DEPRECATED")
        parser.add_argument('--no-daemonize',
                            '-D', '--do-not-daemonize',
                            action='store_false', dest='daemonize',
                            help="DEPRECATED")
        parser.add_argument('-T', '--timeout', metavar='MINUTES', type=int, default=0,
                            help="Optional timeout (in minutes) for use with the 'wait' or 'check' commands.  "
                            "If specified for 'wait', the waiting still stop after the given number of minutes "
                            "and exit with a nonzero code to indicate failure.  If specified for 'check', the "
                            "command will perform some health check based on the given timeout, and exit with "
                            "nonzero code if the check fails.")

        parser.add_argument('--collectd-plugin', default='datasync',
                            help="The `plugin-instance` part of the 'Identifier' "
                            "to be passed to collectd via PUTVAL entries.")

    def run(self, args):
        from rattail.datasync.daemon import DataSyncDaemon

        if args.subcommand == 'wait':
            self.wait(args)

        elif args.subcommand == 'check':
            self.check_queue(args)

        elif args.subcommand == 'check-queue':
            self.check_queue(args)

        elif args.subcommand == 'check-watchers':
            self.check_watchers(args)

        elif args.subcommand == 'collectd':
            self.collectd(args)

        elif args.subcommand == 'remove-settings':
            self.remove_settings(args)

        else: # manage the daemon
            daemon = DataSyncDaemon(args.pidfile, config=self.config)
            if args.subcommand == 'stop':
                daemon.stop()
            else: # start
                try:
                    daemon.start(daemonize=False)
                except KeyboardInterrupt:
                    self.stderr.write("Interrupted.\n")

    def wait(self, args):
        model = self.model
        session = self.make_session()
        started = make_utc()
        log.debug("will wait for current change queue to clear")
        last_logged = started

        changes = session.query(model.DataSyncChange)
        count = changes.count()
        log.debug("there are %d changes in the queue", count)
        while count:
            try:
                now = make_utc()

                if args.timeout and (now - started).seconds >= (args.timeout * 60):
                    log.warning("datasync wait timed out after %d minutes, with %d changes in queue",
                                args.timeout, count)
                    sys.exit(1)

                if (now - last_logged).seconds >= 60:
                    log.debug("still waiting, %d changes in the datasync queue", count)
                    last_logged = now

                time.sleep(1)
                count = changes.count()

            except KeyboardInterrupt:
                self.stderr.write("Waiting cancelled by user\n")
                session.close()
                sys.exit(1)

        session.close()
        log.debug("all datasync changes have been processed")

    def check_queue(self, args):
        """
        Perform general queue / health check for datasync.
        """
        model = self.model
        session = self.make_session()

        # looking for changes which have been around for "timeout" minutes
        timeout = args.timeout or 90
        cutoff = make_utc() - datetime.timedelta(seconds=60 * timeout)
        changes = session.query(model.DataSyncChange)\
                         .filter(model.DataSyncChange.obtained < cutoff)\
                         .count()
        session.close()

        # if we found stale changes, then "fail" - otherwise we'll "succeed"
        if changes:
            # TODO: should log set of unique payload types, for troubleshooting
            log.debug("found %s changes, in queue for %s minutes", changes, timeout)
            self.stderr.write("Found {} changes, in queue for {} minutes\n".format(changes, timeout))
            sys.exit(1)

        log.info("found no changes in queue for %s minutes", timeout)

    def check_watchers(self, args):
        """
        Perform general health check for datasync watcher threads.
        """
        from rattail.datasync.config import load_profiles
        from rattail.datasync.util import get_lastrun

        profiles = load_profiles(self.config)
        session = self.make_session()

        # cutoff is "timeout" minutes before "now"
        timeout = args.timeout or 15
        cutoff = make_utc() - datetime.timedelta(seconds=60 * timeout)

        dead = []
        for key in profiles:

            # looking for watcher "last run" time older than "timeout" minutes
            lastrun = get_lastrun(self.config, key, tzinfo=False, session=session)
            if lastrun and lastrun < cutoff:
                dead.append(key)

        session.close()

        # if we found dead watchers, then "fail" - otherwise we'll "succeed"
        if dead:
            self.stderr.write("Found {} watcher threads dead for {} minutes: {}\n".format(len(dead), timeout, ', '.join(dead)))
            sys.exit(1)

        log.info("found no watcher threads dead for %s minutes", timeout)

    def collectd(self, args):
        """
        Output statistics for collectd
        """
        from rattail.datasync.config import load_profiles
        from rattail.datasync.util import get_lastrun

        plugin = args.collectd_plugin
        profiles = load_profiles(self.config)
        session = self.app.make_session()
        model = self.model

        # current time (sanity check)
        now = localtime(self.config)
        self.collectd_putval(plugin, 'gauge-current_time',
                             now.timestamp(), now=now)

        # iterate watcher profiles
        for key in profiles:

            # last run for watcher
            lastrun = get_lastrun(self.config, key, local=True, tzinfo=True,
                                  session=session)
            self.collectd_putval(plugin, 'gauge-{}_watcher_lastrun'.format(key),
                                 lastrun.timestamp(), now=now)

            # seconds since last run
            self.collectd_putval(plugin, 'gauge-{}_watcher_seconds_since_lastrun'.format(key),
                                 now.timestamp() - lastrun.timestamp(), now=now)

        # now inspect the change queue..

        # total changes in queue
        total = session.query(model.DataSyncChange).count()
        self.collectd_putval(plugin, 'gauge-queue_changes_total',
                             total, now=now)

        # stale changes in queue
        timeout = self.config.getint('rattail.datasync',
                                     'collectd.changes_stale_timeout',
                                     default=15) # minutes
        cutoff = make_utc() - datetime.timedelta(seconds=60 * timeout)
        stale = session.query(model.DataSyncChange)\
                       .filter(model.DataSyncChange.obtained < cutoff)\
                       .count()
        self.collectd_putval(plugin, 'gauge-queue_changes_stale',
                             stale, now=now)
        self.collectd_putval(plugin, 'gauge-queue_changes_stale_timeout',
                             timeout, now=now)

        session.close()

    def collectd_putval(self, plugin, data_type, value,
                        hostname=None, interval=None, now=None):
        if not hostname:
            hostname = os.environ.get('COLLECTD_HOSTNAME')
            if not hostname:
                hostname = socket.getfqdn()

        if not interval:
            interval = os.environ.get('COLLECTD_INTERVAL')
        if interval:
            interval = ' interval={}'.format(interval)
        else:
            interval = ''

        if now:
            value = '{}:{}'.format(now.timestamp(), value)
        else:
            value = 'N:{}'.format(value)

        msg = 'PUTVAL {}/{}/{}{} {}\n'.format(
            hostname,
            plugin,
            data_type,
            interval,
            value)

        sys.stdout.write(msg)

    def remove_settings(self, args):
        """
        Remove all datasync settings from the DB
        """
        from rattail.datasync.util import purge_datasync_settings

        session = self.app.make_session()
        purge_datasync_settings(self.config, session)
        session.commit()
        session.close()
