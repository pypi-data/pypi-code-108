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
DataSync Configuration
"""

from __future__ import unicode_literals, absolute_import

import re
import logging

from rattail.config import ConfigProfile
from rattail.util import load_object
from rattail.exceptions import ConfigurationError

from rattail.datasync.watchers import NullWatcher


log = logging.getLogger(__name__)


class DataSyncProfile(ConfigProfile):
    """
    Simple class to hold configuration for a DataSync "profile".  Each profile
    determines which database(s) will be watched for new changes, and which
    consumer(s) will then be instructed to process the changes.

    .. todo::
       This clearly needs more documentation.
    """
    section = 'rattail.datasync'

    def __init__(self, *args, **kwargs):
        load_disabled_consumers = kwargs.pop('load_disabled_consumers', False)
        super(DataSyncProfile, self).__init__(*args, **kwargs)

        self.watcher_spec = self._config_string('watcher')
        if self.watcher_spec == 'null':
            self.watcher = NullWatcher(self.config, self.key)
        else:
            dbkey = self._config_string('watcher.db', default='default')
            kwargs = {'dbkey': dbkey}
            pattern = re.compile(r'^{}\.watcher\.kwarg\.(?P<keyword>\w+)$'.format(self.key))
            # TODO: this should not be referencing the config parser directly?
            # (but we have no other way yet, to know which options are defined)
            # (we should at least allow config to be defined in DB Settings)
            # (however that should be optional, since some may not have a DB)
            if self.config.parser.has_section(self.section):
                for option in self.config.parser.options(self.section):
                    match = pattern.match(option)
                    if match:
                        keyword = match.group('keyword')
                        kwargs[keyword] = self.config.get(self.section, option)
            self.watcher = load_object(self.watcher_spec)(self.config, self.key, **kwargs)
        self.watcher.delay = self._config_int('watcher.delay', default=self.watcher.delay)
        self.watcher.retry_attempts = self._config_int('watcher.retry_attempts', default=self.watcher.retry_attempts)
        self.watcher.retry_delay = self._config_int('watcher.retry_delay', default=self.watcher.retry_delay)
        self.watcher.default_runas = self._config_string('consumers.runas')

        consumers = self._config_list('consumers')
        if consumers == ['self']:
            self.watcher.consumes_self = True
        else:
            self.watcher.consumes_self = False
            self.consumer_delay = self._config_int('consumer_delay', default=1)
            self.consumers = self.normalize_consumers(self.watcher.default_runas,
                                                      include_disabled=load_disabled_consumers)
            self.watcher.consumer_stub_keys = [c.key for c in self.consumers]

    def normalize_consumers(self, default_runas, include_disabled=False):
        consumers = []
        if include_disabled:
            enabled = get_consumer_keys(self.config, self.key,
                                        include_disabled=False)
        for key in get_consumer_keys(self.config, self.key,
                                     include_disabled=include_disabled):
            consumer_spec = self._config_string('consumer.{}'.format(key))
            if consumer_spec == 'null':
                consumer_spec = 'rattail.datasync.consumers:NullTestConsumer'
            dbkey = self._config_string('consumer.{}.db'.format(key),
                                        default='default')
            runas = self._config_string('consumer.{}.runas'.format(key))
            try:
                consumer = load_object(consumer_spec)(self.config, key, dbkey=dbkey,
                                                      runas=runas or default_runas,
                                                      watcher=self.watcher)
            except:
                log.debug("failed to load '%s' consumer for '%s' profile",
                          key, self.key, exc_info=True)
                if not include_disabled:
                    raise
            else:
                consumer.spec = consumer_spec
                consumer.delay = self._config_int(
                    'consumer.{}.delay'.format(key),
                    default=self.consumer_delay)
                consumer.retry_attempts = self._config_int(
                    'consumer.{}.retry_attempts'.format(key),
                    default=consumer.retry_attempts)
                consumer.retry_delay = self._config_int(
                    'consumer.{}.retry_delay'.format(key),
                    default=consumer.retry_delay)
                if include_disabled:
                    consumer.enabled = key in enabled
                consumers.append(consumer)
        return consumers


def get_consumer_keys(config, profile_key, include_disabled=False):

    # start with the primary set of consumer keys
    keys = config.getlist('rattail.datasync', '{}.consumers'.format(profile_key))

    if include_disabled:

        # first look in config file options
        if config.parser.has_section('rattail.datasync'):

            # find all consumers with spec defined
            pattern = re.compile(r'^{}\.consumer\.([^.]+)$'.format(profile_key))
            for option in config.parser.options('rattail.datasync'):
                match = pattern.match(option)
                if match:
                    keys.append(match.group(1))

        # maybe also look for config settings in DB
        if config.usedb:
            app = config.get_app()
            model = config.get_model()
            session = app.make_session()
            settings = session.query(model.Setting)\
                              .filter(model.Setting.name.like('rattail.datasync.{}.consumer.%'.format(profile_key)))\
                              .all()
            pattern = re.compile(r'^rattail\.datasync\.{}\.consumer\.([^.]+)$')
            for setting in settings:
                match = pattern.match(setting.name)
                if match:
                    keys.append(match.group(1))
            session.close()

    return list(sorted(set(keys)))


def get_profile_keys(config, include_disabled=False):
    """
    Returns a list of profile keys used in the DataSync configuration.
    """
    # start with the primary set of watcher keys
    keys = config.getlist('rattail.datasync', 'watch',
                          default=[])

    if include_disabled:

        # first look in config file options
        if config.parser.has_section('rattail.datasync'):

            # find all profiles with watcher defined
            pattern = re.compile(r'^(\S+)\.watcher$')
            for option in config.parser.options('rattail.datasync'):
                match = pattern.match(option)
                if match:
                    keys.append(match.group(1))

        # maybe also look for config settings in DB
        if config.usedb:
            app = config.get_app()
            model = config.get_model()
            session = app.make_session()
            settings = session.query(model.Setting)\
                              .filter(model.Setting.name.like('rattail.datasync.%.watcher'))\
                              .all()
            for setting in settings:
                parts = setting.name.split('.')
                keys.append('.'.join(parts[2:-1]))
            session.close()

    return list(sorted(set(keys)))


def load_profiles(config, include_disabled=False, ignore_problems=False):
    """
    Load all DataSync profiles defined within configuration.

    :param include_disabled: If true, then disabled profiles will be
       included in the return value; otherwise only currently-enabled
       profiles are returned.
    """
    # Make sure we have a top-level directive.
    keys = get_profile_keys(config, include_disabled=include_disabled)
    if not keys and not ignore_problems:
        raise ConfigurationError(
            "The DataSync configuration does not specify any profiles "
            "to be watched.  Please defined the 'watch' option within "
            "the [rattail.datasync] section of your config file.")

    if include_disabled:
        enabled = get_profile_keys(config, include_disabled=False)

    profiles = {}
    for key in keys:

        if include_disabled:
            try:
                profile = DataSyncProfile(config, key,
                                          load_disabled_consumers=True)
            except Exception as error:
                log.debug("could not create '%s' profile", key, exc_info=True)
                pass
            else:
                profile.enabled = key in enabled
                profiles[key] = profile

        else:
            profile = DataSyncProfile(config, key)
            profile.enabled = True
            profiles[key] = profile

    return profiles
