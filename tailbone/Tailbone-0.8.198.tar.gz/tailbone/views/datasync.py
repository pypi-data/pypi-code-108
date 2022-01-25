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
DataSync Views
"""

from __future__ import unicode_literals, absolute_import

import getpass
import json
import subprocess
import logging

from rattail.db import model
from rattail.datasync.config import load_profiles
from rattail.datasync.util import purge_datasync_settings

from tailbone.views import MasterView


log = logging.getLogger(__name__)


class DataSyncThreadView(MasterView):
    """
    Master view for DataSync itself.

    This should (eventually) show all running threads in the main
    index view, with status for each, sort of akin to "dashboard".
    For now it only serves the config view.
    """
    normalized_model_name = 'datasyncthread'
    model_title = "DataSync Thread"
    model_key = 'key'
    route_prefix = 'datasync'
    url_prefix = '/datasync'
    viewable = False
    creatable = False
    editable = False
    deletable = False
    filterable = False
    pageable = False

    configurable = True
    config_title = "DataSync"

    grid_columns = [
        'key',
    ]

    def get_data(self, session=None):
        data = []
        return data

    def restart(self):
        cmd = self.rattail_config.getlist('tailbone', 'datasync.restart',
                                          # nb. simulate by default
                                          default='/bin/sleep 3')
        log.debug("attempting datasync restart with command: %s", cmd)
        result = subprocess.call(cmd)
        if result == 0:
            self.request.session.flash("DataSync daemon has been restarted.")
        else:
            self.request.session.flash("DataSync daemon could not be restarted; result was: {}".format(result), 'error')
        return self.redirect(self.request.get_referrer(default=self.request.route_url('datasyncchanges')))

    def configure_get_context(self):
        profiles = load_profiles(self.rattail_config,
                                 include_disabled=True,
                                 ignore_problems=True)

        profiles_data = []
        for profile in sorted(profiles.values(), key=lambda p: p.key):
            data = {
                'key': profile.key,
                'watcher_spec': profile.watcher_spec,
                'watcher_dbkey': profile.watcher.dbkey,
                'watcher_delay': profile.watcher.delay,
                'watcher_retry_attempts': profile.watcher.retry_attempts,
                'watcher_retry_delay': profile.watcher.retry_delay,
                'watcher_default_runas': profile.watcher.default_runas,
                'watcher_consumes_self': profile.watcher.consumes_self,
                # 'notes': None,   # TODO
                'enabled': profile.enabled,
            }

            consumers = []
            if profile.watcher.consumes_self:
                pass
            else:
                for consumer in sorted(profile.consumers, key=lambda c: c.key):
                    consumers.append({
                        'key': consumer.key,
                        'consumer_spec': consumer.spec,
                        'consumer_dbkey': consumer.dbkey,
                        'consumer_runas': getattr(consumer, 'runas', None),
                        'consumer_delay': consumer.delay,
                        'consumer_retry_attempts': consumer.retry_attempts,
                        'consumer_retry_delay': consumer.retry_delay,
                        'enabled': consumer.enabled,
                    })
            data['consumers_data'] = consumers
            profiles_data.append(data)

        return {
            'profiles': profiles,
            'profiles_data': profiles_data,
            'restart_command': self.rattail_config.get('tailbone', 'datasync.restart'),
            'system_user': getpass.getuser(),
        }

    def configure_gather_settings(self, data):
        settings = []
        watch = []

        for profile in json.loads(data['profiles']):
            pkey = profile['key']
            if profile['enabled']:
                watch.append(pkey)

            settings.extend([
                {'name': 'rattail.datasync.{}.watcher'.format(pkey),
                 'value': profile['watcher_spec']},
                {'name': 'rattail.datasync.{}.watcher.db'.format(pkey),
                 'value': profile['watcher_dbkey']},
                {'name': 'rattail.datasync.{}.watcher.delay'.format(pkey),
                 'value': profile['watcher_delay']},
                {'name': 'rattail.datasync.{}.watcher.retry_attempts'.format(pkey),
                 'value': profile['watcher_retry_attempts']},
                {'name': 'rattail.datasync.{}.watcher.retry_delay'.format(pkey),
                 'value': profile['watcher_retry_delay']},
                {'name': 'rattail.datasync.{}.consumers.runas'.format(pkey),
                 'value': profile['watcher_default_runas']},
            ])

            consumers = []
            if profile['watcher_consumes_self']:
                consumers = ['self']
            else:

                for consumer in profile['consumers_data']:
                    ckey = consumer['key']
                    if consumer['enabled']:
                        consumers.append(ckey)
                    settings.extend([
                        {'name': 'rattail.datasync.{}.consumer.{}'.format(pkey, ckey),
                         'value': consumer['consumer_spec']},
                        {'name': 'rattail.datasync.{}.consumer.{}.db'.format(pkey, ckey),
                         'value': consumer['consumer_dbkey']},
                        {'name': 'rattail.datasync.{}.consumer.{}.delay'.format(pkey, ckey),
                         'value': consumer['consumer_delay']},
                        {'name': 'rattail.datasync.{}.consumer.{}.retry_attempts'.format(pkey, ckey),
                         'value': consumer['consumer_retry_attempts']},
                        {'name': 'rattail.datasync.{}.consumer.{}.retry_delay'.format(pkey, ckey),
                         'value': consumer['consumer_retry_delay']},
                        {'name': 'rattail.datasync.{}.consumer.{}.runas'.format(pkey, ckey),
                         'value': consumer['consumer_runas']},
                    ])

            settings.extend([
                {'name': 'rattail.datasync.{}.consumers'.format(pkey),
                 'value': ', '.join(consumers)},
            ])

        if watch:
            settings.append({'name': 'rattail.datasync.watch',
                             'value': ', '.join(watch)})

        settings.append({'name': 'tailbone.datasync.restart',
                         'value': data['restart_command']})

        return settings

    def configure_remove_settings(self):
        purge_datasync_settings(self.rattail_config, self.Session())

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._datasync_defaults(config)

    @classmethod
    def _datasync_defaults(cls, config):
        permission_prefix = cls.get_permission_prefix()
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()

        # restart
        config.add_tailbone_permission(permission_prefix,
                                       '{}.restart'.format(permission_prefix),
                                       label="Restart the DataSync daemon")
        config.add_route('{}.restart'.format(route_prefix),
                         '{}/restart'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='restart',
                        route_name='{}.restart'.format(route_prefix),
                        permission='{}.restart'.format(permission_prefix))


class DataSyncChangeView(MasterView):
    """
    Master view for the DataSyncChange model.
    """
    model_class = model.DataSyncChange
    url_prefix = '/datasync/changes'
    permission_prefix = 'datasync_changes'
    creatable = False
    bulk_deletable = True

    labels = {
        'batch_id': "Batch ID",
    }

    grid_columns = [
        'source',
        'batch_id',
        'batch_sequence',
        'payload_type',
        'payload_key',
        'deletion',
        'obtained',
        'consumer',
    ]

    def configure_grid(self, g):
        super(DataSyncChangeView, self).configure_grid(g)

        # batch_sequence
        g.set_label('batch_sequence', "Batch Seq.")
        g.filters['batch_sequence'].label = "Batch Sequence"

        g.set_sort_defaults('obtained')
        g.set_type('obtained', 'datetime')

    def template_kwargs_index(self, **kwargs):
        kwargs['allow_filemon_restart'] = bool(self.rattail_config.get('tailbone', 'filemon.restart'))
        return kwargs

    def configure_form(self, f):
        super(DataSyncChangeView, self).configure_form(f)

        f.set_readonly('obtained')


# TODO: deprecate / remove this
DataSyncChangesView = DataSyncChangeView


def includeme(config):
    DataSyncThreadView.defaults(config)
    DataSyncChangeView.defaults(config)
