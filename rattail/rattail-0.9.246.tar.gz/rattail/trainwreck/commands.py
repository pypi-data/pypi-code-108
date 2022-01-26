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
Trainwreck commands
"""

from __future__ import unicode_literals, absolute_import

import datetime
import sys
import logging
import warnings

import sqlalchemy as sa

from rattail import __version__
from rattail import commands
from rattail.time import localtime, date_range
from rattail.util import load_object


log = logging.getLogger(__name__)


def main(*args):
    """
    Primary entry point for Trainwreck command system
    """
    if args:
        args = list(args)
    else:
        args = sys.argv[1:]

    cmd = Command()
    cmd.run(*args)


class Command(commands.Command):
    """
    Primary command for Trainwreck
    """
    name = 'trainwreck'
    version = __version__
    description = "Trainwreck -- Transaction data warehouse"
    long_description = ""


class ImportToTrainwreck(commands.ImportSubcommand):
    """
    Generic base class for commands which import *to* a Trainwreck DB.
    """
    # TODO: deprecate / remove this
    default_handler_spec = None

    # TODO: deprecate / remove this
    def get_handler_factory(self, **kwargs):

        # only do this nonsense if we still have old-style default
        if self.default_handler_spec:

            if self.config:
                # TODO: this one needs some work
                spec = self.config.get('trainwreck.importing', '{}.handler'.format(self.handler_key))
                if not spec:
                    spec = self.config.get('rattail.trainwreck.importing', '{}.handler'.format(self.handler_key))
                    if spec:
                        warnings.warn(("Handler override uses deprecated config.  "
                                       "Please change the setting name used, from "
                                       "`[rattail.trainwreck.importing] {0}.handler` "
                                       "to `[trainwreck.importing] {0}.handler`")\
                                      .format(self.handler_key), DeprecationWarning)
                    else:
                        spec = self.default_handler_spec
            else:
                # just use default, for sake of cmd line help
                spec = self.default_handler_spec
            return load_object(spec)

        # otherwise just do normal logic
        return super(ImportToTrainwreck, self).get_handler_factory(**kwargs)


class ExportTrainwreck(commands.ImportSubcommand):
    """
    Export data to another Trainwreck database
    """
    name = 'export-trainwreck'
    description = __doc__.strip()
    handler_key = 'to_trainwreck.from_trainwreck.export'

    def add_parser_args(self, parser):
        super(ExportTrainwreck, self).add_parser_args(parser)
        parser.add_argument('--dbkey', metavar='KEY',
                            help="Config key for database engine to be used as the \"target\" "
                            "Trainwreck DB, i.e. where data will be exported.  This key must "
                            "be defined in the [trainwreck.db] section of your config file.")

    def get_handler_kwargs(self, **kwargs):
        if 'args' in kwargs:
            kwargs['dbkey'] = kwargs['args'].dbkey
        return kwargs


class ImportTrainwreck(ImportToTrainwreck):
    """
    Import data from another Trainwreck database
    """
    name = 'import-trainwreck'
    description = __doc__.strip()
    handler_key = 'to_trainwreck.from_trainwreck.import'
    accepts_dbkey_param = True

    def add_parser_args(self, parser):
        super(ImportTrainwreck, self).add_parser_args(parser)

        if self.accepts_dbkey_param:
            parser.add_argument('--dbkey', metavar='KEY',
                                help="Config key for database engine to be used as the Trainwreck "
                                "\"host\", i.e. the source of the data to be imported.  This key "
                                "must be defined in the [trainwreck.db] section of your config file.")

    def get_handler_kwargs(self, **kwargs):
        if self.accepts_dbkey_param:
            if 'args' in kwargs:
                kwargs['dbkey'] = kwargs['args'].dbkey
        return kwargs


class Prune(commands.Subcommand):
    """
    Prune some dates from a Trainwreck database
    """
    name = 'prune'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--after', type=commands.date_argument, metavar='DATE',
                            help="Date *after* which all data should be pruned.  If set, no data "
                            "will be pruned from this or earlier dates.  If not set, there will be "
                            "no lower boundary for the prune.")
        parser.add_argument('--before', type=commands.date_argument, metavar='DATE',
                            help="Date *before* which all data should be pruned.  If set, no data "
                            "will be pruned from this or later dates.  If not set, will assume a "
                            "default of \"today\".")

        parser.add_argument('--dbkey', metavar='KEY', default='default',
                            help="Config key for the Trainwreck database engine to be used, i.e. "
                            "from which data should be pruned.  This key must be defined in the "
                            "[trainwreck.db] section of your config file.  Defaults to 'default'.")

        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.")

    def make_trainwreck_session(self):
        """
        Must return a Trainwreck database session, which corresponds to the
        engine represented by the ``self.dbkey`` value.
        """
        from rattail.trainwreck.db import Session

        return Session(bind=self.config.trainwreck_engines[self.dbkey])

    def get_trainwreck_model(self):
        """
        Must return a reference to the Python module which contains Trainwreck
        data models.
        """
        return self.config.get_trainwreck_model()

    def get_earliest_date(self, session):
        """
        Fetches the earliest date which exists in the given session's database.
        Note that this is "calculated" according to ``Transaction.end_time``.
        """
        # TODO: not sure what might happen if there are no transactions with end_time ?
        trainwreck = self.get_trainwreck_model()
        end_time = session.query(sa.func.min(trainwreck.Transaction.end_time)).scalar()
        return localtime(self.config, end_time, from_utc=True).date()

    def prune_date(self, session, date, start_time, end_time):
        """
        Your custom command must implement the logic for this method.  It is
        responsible for fully pruning data from the given session's database,
        for the given date.  The start time and end times given may be used for
        your queries; they are in localtime and are zone-aware.
        """
        raise NotImplementedError

    def run(self, args):
        self.dbkey = args.dbkey
        session = self.make_trainwreck_session()

        if args.after:
            start_date = args.after + datetime.timedelta(days=1)
        else:
            # default is earliest available date
            start_date = self.get_earliest_date(session)

        if args.before:
            end_date = args.before - datetime.timedelta(days=1)
        else:
            # default is yesterday
            end_date = localtime(self.config).date() - datetime.timedelta(days=1)

        for date in date_range(start_date, end_date):
            log.info("pruning from '{}' Trainwreck for {}".format(args.dbkey, date))

            start_time = datetime.datetime.combine(start_date, datetime.time(0))
            start_time = localtime(self.config, start_time)

            end_time = datetime.datetime.combine(end_date + datetime.timedelta(days=1), datetime.time(0))
            end_time = localtime(self.config, end_time)

            self.prune_date(session, date, start_time, end_time)

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        else:
            session.commit()
            log.info("transaction was committed")
        session.close()
