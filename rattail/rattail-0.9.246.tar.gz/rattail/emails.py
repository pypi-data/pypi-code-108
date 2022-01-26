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
Common email config objects
"""

from __future__ import unicode_literals, absolute_import

import sys
import socket
from traceback import format_exception

import six

from rattail.mail import Email
from rattail.util import load_object
from rattail.core import Object
from rattail.time import make_utc, localtime
from rattail.problems import ProblemReport, get_problem_report_handler


class ProblemReportEmail(Email):
    """
    Base class for all "problem report" emails
    """
    abstract = True

    def obtain_sample_data(self, request):
        data = self.sample_data(request)
        handler = get_problem_report_handler(self.config)

        if 'report' not in data:
            reports = handler.get_all_problem_reports()
            email_key = self.__class__.__name__
            for report in reports:
                if report.email_key == email_key:
                    data['report'] = report(self.config)
                    break

            if 'report' not in data:
                report = ProblemReport(self.config)
                report.problem_title = "Generic Title (problem report not found)"
                data['report'] = report

        if 'system_title' not in data:
            system_key = data['report'].system_key or 'rattail'
            data['system_title'] = handler.get_system_title(system_key)

        return data


class datasync_error_watcher_get_changes(Email):
    """
    When any datasync watcher thread encounters an error trying to get changes,
    this email is sent out.
    """
    default_subject = "Watcher failed to get changes"

    def sample_data(self, request):
        from rattail.datasync import DataSyncWatcher
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        watcher = DataSyncWatcher(self.config, 'test')
        watcher.consumes_self = True
        return {
            'watcher': watcher,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
            'datasync_url': '/datasyncchanges',
            'attempts': 2,
        }


class datasync_error_consumer_process_changes(Email):
    """
    When any datasync consumer thread encounters an error trying to process
    changes, this email is sent out.
    """
    default_subject = "Consumer failed to process changes"

    def sample_data(self, request):
        from rattail.datasync import DataSyncWatcher, DataSyncConsumer

        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()

        watcher = DataSyncWatcher(self.config, 'testwatcher')
        consumer = DataSyncConsumer(self.config, 'testconsumer')
        return {
            'watcher': watcher,
            'consumer': consumer,
            'error': exc,
            'attempts': 2,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
            'datasync_url': '/datasync/changes',
        }


class filemon_action_error(Email):
    """
    When any filemon thread encounters an error (and the retry attempts have
    been exhausted) then it will send out this email.
    """
    default_subject = "Error invoking action(s)"

    def sample_data(self, request):
        from rattail.filemon import Action
        action = Action(self.config)
        action.spec = 'rattail.filemon.actions:Action'
        action.retry_delay = 10
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        return {
            'hostname': socket.gethostname(),
            'path': '/tmp/foo.csv',
            'action': action,
            'attempts': 3,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
        }


class new_email_requested(Email):
    """
    Sent when a new email address is requested for a customer,
    e.g. when entering a new customer order.
    """
    default_subject = "Email Update Request"

    def sample_data(self, request):
        model = request.rattail_config.get_model()
        customer = model.Customer(name="Fred Flintstone")
        return {
            'user': request.user,
            'user_display': request.user.display_name,
            'contact': customer,
            'contact_id': '42',
            'email_address': "fred@mailinator.com",
        }


class new_phone_requested(Email):
    """
    Sent when a new phone number is requested for a customer,
    e.g. when entering a new customer order.
    """
    default_subject = "Phone Update Request"

    def sample_data(self, request):
        model = request.rattail_config.get_model()
        customer = model.Customer(name="Fred Flintstone")
        return {
            'user': request.user,
            'user_display': request.user.display_name,
            'contact': customer,
            'contact_id': '42',
            'phone_number': "417-555-1234",
        }


class ImporterEmail(Email):
    """
    Sent when a "version catch-up" import is performed, which involves changes.
    """
    abstract = True
    fallback_key = 'rattail_import_updates'
    handler_spec = None

    def get_handler(self, config):
        return load_object(self.handler_spec)(config)

    def get_default_subject(self, **data):
        host_title = data.get('host_title')
        local_title = data.get('local_title')
        if not (host_title and local_title):
            handler = self.get_handler(self.config)
            if not host_title:
                host_title = handler.host_title
            if not local_title:
                local_title = handler.local_title
        return "Changes for {} -> {}".format(host_title, local_title)

    def sample_data(self, request):
        handler = self.get_handler(request.rattail_config)
        obj = Object()
        local_data = {
            'foo': 42,
            'bar': True,
            'baz': 'something',
        }
        host_data = {
            'foo': 42,
            'bar': False,
            'baz': 'something else',
        }
        return {
            'host_title': handler.host_title,
            'local_title': handler.local_title,
            'direction': 'import',
            'runtime': "1 second",
            'argv': ['bin/rattail', 'import-something'],
            'changes': {
                'Widget': (
                    [],                             # created
                    [(obj, local_data, host_data)], # updated
                    [],                             # deleted
                ),
            },
            'render_record': lambda x: six.text_type(x),
            'max_display': 15,
        }


class rattail_export_rattail_updates(ImporterEmail):
    """
    Sent when a full Rattail -> Rattail data export involves changes.
    """
    handler_spec = 'rattail.importing.rattail:FromRattailToRattailExport'
    abstract = False


class rattail_import_rattail_updates(ImporterEmail):
    """
    Sent when a full Rattail -> Rattail data import involves changes.
    """
    handler_spec = 'rattail.importing.rattail:FromRattailToRattailImport'
    abstract = False


class rattail_import_versions_updates(ImporterEmail):
    """
    Sent when a "version catch-up" import is performed, which involves changes.
    """
    handler_spec = 'rattail.importing.versions:FromRattailToRattailVersions'
    abstract = False


class person_merge_request(Email):
    """
    Sent when a request is submitted to merge two Person records.
    """
    default_subject = "Person Merge Request"

    def sample_data(self, request):
        return {
            'user_display': request.user.display_name,
            'removing_display': "Fred Flintstone",
            'removing_url': '#',
            'keeping_display': "Fred Flintstone",
            'keeping_url': '#',
            'merge_request_url': '#',
        }


class rattail_problems_stale_inventory_batch(ProblemReportEmail):
    """
    Nightly check for "stale" inventory batches, i.e. those created
    but not executed within a certain number of days.
    """
    default_subject = "Stale inventory batches"
    abstract = False

    def sample_data(self, request):
        model = self.config.get_model()
        person = model.Person(display_name="Fred Flintstone")
        user = model.User(username='fred', person=person)
        batch = model.InventoryBatch(id=42, created=self.app.localtime(),
                                     created_by=user)
        return {
            'problems': [batch],
            'cutoff_days': 4,
            'render_time': lambda t: t,
        }


class upgrade_failure(Email):
    """
    Sent when an app upgrade is attempted, but ultimately failed.
    """
    default_subject = "Upgrade Failure"

    def sample_data(self, request):
        upgrade = Object(
            description="upgrade to the latest!",
            notes="nothing special",
            executed=make_utc(),
            executed_by="Fred Flintstone",
            exit_code=42,
        )
        return {
            # TODO: first 3 args should be provided by some common logic instead...
            'rattail_config': self.config,
            'localtime': localtime,
            'app_title': self.config.app_title(),
            'upgrade': upgrade,
            'upgrade_url': '#',
        }


class upgrade_success(Email):
    """
    Sent when an app upgrade is performed successfully.
    """
    default_subject = "Upgrade Success"

    def sample_data(self, request):
        upgrade = Object(
            description="upgrade to the latest!",
            notes="nothing special",
            executed=make_utc(),
            executed_by="Fred Flintstone",
            exit_code=0,
        )
        return {
            # TODO: first 3 args should be provided by some common logic instead...
            'rattail_config': self.config,
            'localtime': localtime,
            'app_title': self.config.app_title(),
            'upgrade': upgrade,
            'upgrade_url': '#',
        }


class user_feedback(Email):
    """
    Sent when a user submits a Feedback form from the web UI.
    """
    default_subject = "User Feedback"

    def sample_data(self, request):
        return {
            'app_title': request.rattail_config.app_title(default="Rattail"),
            'user': None,
            'user_name': "Fred Flintstone",
            'referrer': request.route_url('home'),
            'client_ip': '127.0.0.1',
            'message': "Hey there,\n\njust wondered what the heck was going on with this site?  It's crap.\n\nFred",
        }
