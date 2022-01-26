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
Importing Commands
"""

from __future__ import unicode_literals, absolute_import

import sys
import logging

import six

from rattail.commands.core import Subcommand, date_argument
from rattail.config import parse_list
from rattail.util import load_object
from rattail.core import Object


log = logging.getLogger(__name__)


class ImportSubcommand(Subcommand):
    """
    Base class for subcommands which use the (new) data importing system.
    """
    handler_key = None

    # TODO: should remove this? or perhaps is still useful for simple
    # custom commands to use, which need not worry about inheritance
    # and alternate handlers available etc.
    handler_spec = None

    # TODO: move this into Subcommand or something..
    parent_name = None
    def __init__(self, *args, **kwargs):

        # TODO: should remove this? or perhaps is still useful for
        # simple custom commands to use, which need not worry about
        # inheritance and alternate handlers available etc.
        if 'handler_spec' in kwargs:
            self.handler_spec = kwargs.pop('handler_spec')

        super(ImportSubcommand, self).__init__(*args, **kwargs)
        if self.parent:
            self.parent_name = self.parent.name

    def get_handler_factory(self, **kwargs):
        """
        Should return a Handler factory (e.g. class) which will later
        be called to create a handler instance.
        """
        # TODO: should remove this? or perhaps is still useful for
        # simple custom commands to use, which need not worry about
        # inheritance and alternate handlers available etc.
        if self.handler_spec:
            return load_object(self.handler_spec)

        if self.handler_key:
            handler = self.app.get_import_handler(self.handler_key)
            return type(handler)

        raise RuntimeError("Cannot locate a handler to use!  You "
                           "should probably define `{}.handler_key`"
                           "".format(self.__class__.__name__))

    def get_handler(self, **kwargs):
        """
        Returns a handler instance to be used by the command.
        """
        factory = self.get_handler_factory(args=kwargs.get('args'))
        kwargs.setdefault('config', getattr(self, 'config', None))
        kwargs.setdefault('command', self)
        kwargs.setdefault('progress', self.progress)
        user = self.get_runas_user()
        if user:
            kwargs.setdefault('runas_user', user)
            kwargs.setdefault('runas_username', user.username)
        if 'args' in kwargs:
            args = kwargs['args']
            kwargs.setdefault('dry_run', args.dry_run)
            kwargs.setdefault('collect_changes_for_processing', args.collect_changes)
            if hasattr(args, 'batch_size'):
                kwargs.setdefault('batch_size', args.batch_size)
            if args.max_diffs:
                kwargs.setdefault('diff_max_display', args.max_diffs)
            # kwargs.setdefault('max_create', args.max_create)
            # kwargs.setdefault('max_update', args.max_update)
            # kwargs.setdefault('max_delete', args.max_delete)
            # kwargs.setdefault('max_total', args.max_total)
        kwargs = self.get_handler_kwargs(**kwargs)
        return factory(**kwargs)

    def get_handler_kwargs(self, **kwargs):
        """
        Return a dict of kwargs to be passed to the handler factory.
        """
        return kwargs

    def add_parser_args(self, parser):

        # model names (aka importer keys)
        doc = ("Which data models to import.  If you specify any, then only "
               "data for those models will be imported.  If you do not specify "
               "any, then all *default* models will be imported.")
        parser.add_argument('models', nargs='*', metavar='MODEL', help=doc)

        # make batches
        parser.add_argument('--make-batches', action='store_true',
                            help="If specified, make new Import / Export Batches instead of "
                            "performing an actual (possibly dry-run) import.")

        # key / fields / exclude
        parser.add_argument('--key', metavar='FIELDS',
                            help="List of fields which should be used as \"primary key\" for the import.")
        parser.add_argument('--fields',
                            help="List of fields which should be included in the import.  "
                            "If this parameter is specified, then any field not listed here, "
                            "would be *excluded* regardless of the --exclude-field parameter.")
        parser.add_argument('--exclude-fields',
                            help="List of fields which should be excluded from the import.  "
                            "Any field not listed here, would be included (or not) depending "
                            "on the --fields parameter and/or default importer behavior.")

        # date ranges
        parser.add_argument('--start-date', type=date_argument, metavar='DATE',
                            help="Optional (inclusive) starting point for date range, by which host "
                            "data should be filtered.  Only used by certain importers.")
        parser.add_argument('--end-date', type=date_argument, metavar='DATE',
                            help="Optional (inclusive) ending point for date range, by which host "
                            "data should be filtered.  Only used by certain importers.")
        parser.add_argument('--year', type=int,
                            help="Optional year, by which data should be filtered.  Only used "
                            "by certain importers.")

        # allow create?
        parser.add_argument('--create', action='store_true', default=True,
                            help="Allow new records to be created during the import.")
        parser.add_argument('--no-create', action='store_false', dest='create',
                            help="Do not allow new records to be created during the import.")
        parser.add_argument('--max-create', type=int, metavar='COUNT',
                            help="Maximum number of records which may be created, after which a "
                            "given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # allow update?
        parser.add_argument('--update', action='store_true', default=True,
                            help="Allow existing records to be updated during the import.")
        parser.add_argument('--no-update', action='store_false', dest='update',
                            help="Do not allow existing records to be updated during the import.")
        parser.add_argument('--max-update', type=int, metavar='COUNT',
                            help="Maximum number of records which may be updated, after which a "
                            "given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # allow delete?
        parser.add_argument('--delete', action='store_true', default=False,
                            help="Allow records to be deleted during the import.")
        parser.add_argument('--no-delete', action='store_false', dest='delete',
                            help="Do not allow records to be deleted during the import.")
        parser.add_argument('--max-delete', type=int, metavar='COUNT',
                            help="Maximum number of records which may be deleted, after which a "
                            "given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # collect changes for processing
        parser.add_argument('--collect-changes', action='store_true', default=True,
                            help="Collect changes along the way, for processing "
                            "at the end of the run.  This is on by default as it "
                            "is required for reporting how many changes occurred, "
                            "as well as being used for diff warning emails.")
        parser.add_argument('--no-collect-changes', action='store_false', dest='collect_changes',
                            help="Do *not* collect changes for processing at the "
                            "end of the run.  The main reason for this flag is to "
                            "cut down on memory usage during the run, but it will "
                            "cause the final tally reporting not to work.")

        # max total changes, per model
        parser.add_argument('--max-total', type=int, metavar='COUNT',
                            help="Maximum number of *any* record changes which may occur, after which "
                            "a given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # TODO: deprecate --batch, replace with --batch-size ?
        # batch size
        parser.add_argument('--batch', type=int, dest='batch_size', metavar='SIZE', default=200,
                            help="Split work to be done into batches, with the specified number of "
                            "records in each batch.  Or, set this to 0 (zero) to disable batching. "
                            "Implementation for this may vary somewhat between importers; default "
                            "batch size is 200 records.")

        # treat changes as warnings?
        parser.add_argument('--warnings', '-W', action='store_true',
                            help="Set this flag if you expect a \"clean\" import, and wish for any "
                            "changes which do occur to be processed further and/or specially.  The "
                            "behavior of this flag is ultimately up to the import handler, but the "
                            "default is to send an email notification.")

        # max diffs per warning type
        parser.add_argument('--max-diffs', type=int, metavar='COUNT',
                            help="Maximum number of \"diffs\" to display per warning type, in a "
                            "warning email.  Only used if --warnings is in effect.")

        # dry run?
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.  "
                            "Note that this flag is ignored if --make-batches is specified.")

    def run(self, args):
        log.debug("begin `%s %s` for data models: %s",
                  self.parent_name,
                  self.name,
                  ', '.join(args.models) if args.models else "(ALL)")

        handler = self.get_handler(args=args)
        models = args.models or handler.get_default_keys()
        log.debug("using handler: {}".format(handler))
        log.debug("importing models: {}".format(models))
        log.debug("args are: {}".format(args))

        kwargs = {
            'warnings': args.warnings,
            'fields': parse_list(args.fields),
            'exclude_fields': parse_list(args.exclude_fields),
            'create': args.create,
            'max_create': args.max_create,
            'update': args.update,
            'max_update': args.max_update,
            'delete': args.delete,
            'max_delete': args.max_delete,
            'max_total': args.max_total,
            'progress': self.progress,
            'args': args,
        }
        if args.make_batches:
            kwargs.update({
                'runas_user': self.get_runas_user(),
            })
            handler.make_batches(*models, **kwargs)
        else:
            kwargs.update({
                'key_fields': parse_list(args.key) if args.key else None,
                'dry_run': args.dry_run,
            })
            handler.import_data(*models, **kwargs)

        # TODO: should this logging happen elsewhere / be customizable?
        if args.dry_run:
            log.info("dry run, so transaction was rolled back")
        else:
            log.info("transaction was committed")


# TODO: deprecate / remote this, use ImportFileSubcommand instead
class ImportFromCSV(ImportSubcommand):
    """
    Generic base class for commands which import from a CSV file.
    """

    def add_parser_args(self, parser):
        super(ImportFromCSV, self).add_parser_args(parser)

        parser.add_argument('--source-csv', metavar='PATH', required=True,
                            help="Path to CSV file to be used as data source.")


class ImportFileSubcommand(ImportSubcommand):
    """
    Base class for import commands which use data file(s) as source
    """

    def add_parser_args(self, parser):
        super(ImportFileSubcommand, self).add_parser_args(parser)

        parser.add_argument('--input-dir', metavar='PATH', required=True,
                            help="Directory from which input files should be read.  "
                            "Note that this is a *required* parameter.")

    def get_handler_kwargs(self, **kwargs):
        kwargs = super(ImportFileSubcommand, self).get_handler_kwargs(**kwargs)

        if 'args' in kwargs:
            args = kwargs['args']
            kwargs['input_dir'] = args.input_dir

        return kwargs


class ImportCSV(ImportFileSubcommand):
    """
    Import data from CSV file(s) to Rattail database
    """
    name = 'import-csv'
    description = __doc__.strip()
    handler_key = 'to_rattail.from_csv.import'


class ImportIFPS(ImportFileSubcommand):
    """
    Import data from IFPS file(s) to Rattail database
    """
    name = 'import-ifps'
    description = __doc__.strip()
    handler_key = 'to_rattail.from_ifps.import'


class ExportFileSubcommand(ImportSubcommand):
    """
    Base class for export commands which target data file(s)
    """

    def add_parser_args(self, parser):
        super(ExportFileSubcommand, self).add_parser_args(parser)

        parser.add_argument('--output-dir', metavar='PATH', required=True,
                            help="Directory to which output files should be written.  "
                            "Note that this is a *required* parameter.")

    def get_handler_kwargs(self, **kwargs):
        kwargs = super(ExportFileSubcommand, self).get_handler_kwargs(**kwargs)

        if 'args' in kwargs:
            args = kwargs['args']
            kwargs['output_dir'] = args.output_dir

        return kwargs


class ExportCSV(ExportFileSubcommand):
    """
    Export data from Rattail to CSV file(s)
    """
    name = 'export-csv'
    description = __doc__.strip()
    handler_key = 'to_csv.from_rattail.export'


class ExportRattail(ImportSubcommand):
    """
    Export data to another Rattail database
    """
    name = 'export-rattail'
    description = __doc__.strip()
    handler_key = 'to_rattail.from_rattail.export'
    default_dbkey = 'host'

    def add_parser_args(self, parser):
        super(ExportRattail, self).add_parser_args(parser)
        parser.add_argument('--dbkey', metavar='KEY', default=self.default_dbkey,
                            help="Config key for database engine to be used as the \"target\" "
                            "Rattail system, i.e. where data will be exported.  This key must "
                            "be defined in the [rattail.db] section of your config file.")

    def get_handler_kwargs(self, **kwargs):
        if 'args' in kwargs:
            kwargs['dbkey'] = kwargs['args'].dbkey
        return kwargs


class ImportToRattail(ImportSubcommand):
    """
    Generic base class for commands which import *to* a Rattail system.
    """


class ImportRattail(ImportToRattail):
    """
    Import data from another Rattail database
    """
    name = 'import-rattail'
    description = __doc__.strip()
    handler_key = 'to_rattail.from_rattail.import'
    accepts_dbkey_param = True

    def add_parser_args(self, parser):
        super(ImportRattail, self).add_parser_args(parser)
        if self.accepts_dbkey_param:
            parser.add_argument('--dbkey', metavar='KEY', default='host',
                                help="Config key for database engine to be used as the Rattail "
                                "\"host\", i.e. the source of the data to be imported.  This key "
                                "must be defined in the [rattail.db] section of your config file.  "
                                "Defaults to 'host'.")

    def get_handler_kwargs(self, **kwargs):
        if self.accepts_dbkey_param:
            if 'args' in kwargs:
                kwargs['dbkey'] = kwargs['args'].dbkey
        return kwargs


class ImportRattailBulk(ImportRattail):
    """
    Bulk-import data from another Rattail database
    """
    name = 'import-rattail-bulk'
    description = __doc__.strip()
    handler_key = 'to_rattail.from_rattail_bulk.import'


class ImportSampleData(ImportToRattail):
    """
    Import sample data to a Rattail database
    """
    name = 'import-sample'
    description = __doc__.strip()
    handler_key = 'to_rattail.from_sample.import'


class ImportVersions(ImportRattail):
    """
    Make initial versioned records for data models
    """
    name = 'import-versions'
    description = __doc__.strip()
    handler_key = 'to_rattail_versions.from_rattail.import'
    accepts_dbkey_param = False
    default_comment = "import catch-up versions"

    def add_parser_args(self, parser):
        super(ImportVersions, self).add_parser_args(parser)
        parser.add_argument('--comment', '-m', type=six.text_type, default=self.default_comment,
                            help="Comment to be recorded with the transaction.  "
                            "Default is \"{}\".".format(self.default_comment))

    def get_handler_kwargs(self, **kwargs):
        if 'args' in kwargs:
            kwargs['comment'] = kwargs['args'].comment
        return kwargs

    def run(self, args):
        if not self.config.versioning_has_been_enabled:
            self.stderr.write("Continuum versioning is not enabled, "
                              "per config and/or command line args\n")
            sys.exit(1)
        super(ImportVersions, self).run(args)


class VersionSubcommand(Subcommand):
    """
    Base class for subcommands which act on version data
    """

    def add_parser_args(self, parser):

        parser.add_argument('--list', '-l', action='store_true',
                            help="Show list of all model names, for which version tables exist.")

        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.")

    def collect_models(self):
        """
        Gather and return a dict of data model classes, for which version
        tables exist.
        """
        import sqlalchemy_continuum as continuum

        model = self.model

        # first we collect names of "potential" model classes
        names = []
        for name in dir(model):
            obj = getattr(model, name)
            if isinstance(obj, type):
                if issubclass(obj, model.Base):
                    names.append(name)

        # next we find out if each has a version class
        models = {}
        for name in sorted(names):
            cls = getattr(model, name)
            try:
                vcls = continuum.version_class(cls)
            except continuum.ClassNotVersioned:
                pass
            else:
                models[name] = cls

        return models

    def list_models(self):
        """
        Display a list of all version tables in the DB.
        """
        models = self.collect_models()
        if models:
            for name in sorted(models):
                self.stdout.write("{}\n".format(name))
        else:
            log.warning("hm, no version classes found; is versioning enabled?")


class PurgeVersions(VersionSubcommand):
    """
    Purge version data for some or all tables
    """
    name = 'purge-versions'
    description = __doc__.strip()

    def run(self, args):
        if not self.config.versioning_enabled():
            self.stderr.write("Continuum versioning is not enabled, per config\n")
            sys.exit(1)

        if args.list:
            self.list_models()

        else:
            session = self.make_session()
            self.purge_models(session)
            if args.dry_run:
                session.rollback()
                log.info("dry run, so transaction was aborted")
            else:
                session.commit()
                log.info("transaction was committed")
            session.close()

    def purge_models(self, session):
        """
        Purge version data for all given models.
        """
        models = self.collect_models()
        if not models:
            log.warning("i have no models to purge!")
            return

        for name, cls in sorted(six.iteritems(models)):
            self.purge_version_data(session, cls)

        self.stdout.write("purged all data for {} version tables\n".format(len(models)))

        log.debug("will now purge data for transaction_meta table")
        session.execute('truncate "transaction_meta"')
        log.debug("will now purge data for transaction table")
        session.execute('truncate "transaction"')
        self.stdout.write("purged all data for 2 transaction tables\n")

    def purge_version_data(self, session, cls):
        """
        Purge version data for the given model class.
        """
        import sqlalchemy_continuum as continuum

        vcls = continuum.version_class(cls)
        vtable = vcls.__table__

        log.debug("will now purge data for version table: %s", vtable.name)
        session.execute('truncate "{}"'.format(vtable.name))
        self.stdout.write("purged data for: {}\n".format(vtable.name))


class VersionCheck(VersionSubcommand):
    """
    Run consistency checks for version data tables
    """
    name = 'version-check'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        super(VersionCheck, self).add_parser_args(parser)

        parser.add_argument('models', nargs='*', metavar='MODEL',
                            help="Which data models to check.  If you specify any, then only "
                            "data for those models will be checked.  If you do not specify "
                            "any, then all supported models will be checked.")

    def run(self, args):
        if not self.config.versioning_enabled():
            self.stderr.write("Continuum versioning is not enabled, per config\n")
            sys.exit(1)

        if args.list:
            self.list_models()

        else:
            session = self.make_session()
            self.run_version_checks(session, args.models)
            self.finalize_session(session, dry_run=args.dry_run)

    def run_version_checks(self, session, models):
        """
        Run version data checks for all given models.
        """
        requested = models
        all_models = self.collect_models()
        if requested:
            models = dict([(k, v)
                           for k, v in six.iteritems(all_models)
                           if k in requested])
        else:
            models = all_models
        if not models:
            log.warning("i have no models to check!")
            return

        for name, cls in sorted(six.iteritems(models)):
            self.check_versions(session, cls)

        log.info("checked version data for %s models", len(models))

    def check_versions(self, session, cls):
        """
        Check version data for the given model class.
        """
        import sqlalchemy_continuum as continuum

        model_name = cls.__name__
        log.debug("will now check version data for model: %s", model_name)

        vcls = continuum.version_class(cls)
        versions = session.query(vcls).all()
        versions_by_uuid = {}
        result = Object(problems=0)

        def organize(version, i):
            versions_by_uuid.setdefault(version.uuid, []).append(version)

        self.progress_loop(organize, versions,
                           message="Organizing version data for {}".format(model_name))

        def check(uuid, i):
            versions = versions_by_uuid[uuid]
            created = [v for v in versions
                       if v.operation_type == continuum.Operation.INSERT]
            if len(created) != 1:
                log.warning("should be 1 INSERT for %s %s, but found %s",
                            model_name, uuid, len(created))
                result.problems += 1

        self.progress_loop(check, list(versions_by_uuid.keys()),
                           message="Checking version data for {}".format(model_name))

        log.info("found %s problems for model: %s", result.problems, model_name)
