# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
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
Commands related to purging of old data
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import shutil
import logging

from rattail.commands.core import Subcommand, date_argument
from rattail.core import Object
from rattail.time import localtime, make_utc


log = logging.getLogger(__name__)


class PurgeSubcommand(Subcommand):
    """
    Base class for subcommands which purge old data
    """
    purge_title = "Object"
    default_before_days = 90

    @property
    def purge_title_plural(self):
        return "{}s".format(self.purge_title)

    def add_parser_args(self, parser):
        super(PurgeSubcommand, self).add_parser_args(parser)

        parser.add_argument('--before', type=date_argument, metavar='DATE',
                            help="Use this date as cutoff, i.e. purge all data "
                            "*before* this date.  If not specified, will use "
                            "--before-days to calculate instead.")

        parser.add_argument('--before-days', type=int, metavar='DAYS',
                            default=self.default_before_days,
                            help="Calculate the cutoff date by subtracting this "
                            "number of days from the current date, i.e. purge all "
                            "data *before* the resulting date.  Note that if you "
                            "specify --before then that date will be used instead "
                            "of calculating one from --before-days.  If neither is "
                            "specified then --before-days is used, with its default "
                            "value of 90 days.")

        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging "
                            "etc. to occur, but rollback (abort) the transaction "
                            "at the end.")

    def run(self, args):
        log.info("will purge things of type: %s", self.purge_title)

        if args.before and args.before_days != self.default_before_days:
            log.warning("specifying both --before and --before-days is "
                        "redundant; --before will take precedence.")

        session = self.make_session()

        # calculate our cutoff date
        if args.before:
            cutoff = args.before
        else:
            today = localtime(self.config).date()
            cutoff = today - datetime.timedelta(days=args.before_days)
        cutoff = datetime.datetime.combine(cutoff, datetime.time(0))
        cutoff = localtime(self.config, cutoff)
        log.info("using %s as cutoff date", cutoff.date())

        # find things, and purge them
        things = self.find_things_to_purge(session, cutoff,
                                           dry_run=args.dry_run)
        log.info("found %s thing(s) to purge", len(things or []))
        if things:
            purged = self.purge_things(session, things, cutoff,
                                       dry_run=args.dry_run)
            log.info("%spurged %s %s",
                     "(would have) " if args.dry_run else "",
                     purged, self.purge_title_plural)

        self.finalize_session(session, dry_run=args.dry_run)
        session.close()

    def find_things_to_purge(self, session, cutoff, dry_run=False):
        pass

    def purge_things(self, session, things, cutoff, dry_run=False):
        result = Object(purged=0)

        def purge(thing, i):
            if self.purge_thing(session, thing, cutoff,
                                dry_run=dry_run):
                result.purged += 1
            if i % 200 == 0:
                session.flush()

        self.progress_loop(purge, things,
                           message="Purging {}".format(self.purge_title_plural))
        return result.purged

    def purge_thing(self, session, thing, cutoff, dry_run=False):
        """
        This method should contain logic which actually "purges" something.
        """
        log.info("purging object: %s", thing)
        return True


class PurgeExport(PurgeSubcommand):
    """
    Base classes for data which purge "export" objects
    """

    @property
    def purge_model_class(self):
        raise NotImplementedError("You must define %s.purge_model_class",
                                  self.__class__.__name__)

    @property
    def purge_title(self):
        return self.purge_model_class.get_model_title()

    @property
    def purge_title_plural(self):
        return self.purge_model_class.get_model_title_plural()

    def find_things_to_purge(self, session, cutoff, dry_run=False):
        model = self.model
        exports = session.query(self.purge_model_class)\
                         .filter(self.purge_model_class.created < make_utc(cutoff))\
                         .all()
        return exports

    def purge_thing(self, session, export, cutoff, dry_run=False):
        """
        This method does the basics, i.e. deleting the export record from the
        database session, and (if not dry-run) deleting any associated files
        from disk.
        """
        uuid = export.uuid
        log.debug("purging export object %s: %s", uuid, export)
        session.delete(export)

        # maybe delete associated files
        if not dry_run:
            session.flush()
            key = self.purge_model_class.export_key
            path = self.config.export_filepath(key, uuid)
            if os.path.exists(path):
                shutil.rmtree(path)

        return True
