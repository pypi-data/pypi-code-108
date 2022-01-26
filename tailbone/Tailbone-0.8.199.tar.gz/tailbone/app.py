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
Application Entry Point
"""

from __future__ import unicode_literals, absolute_import

import os
import warnings

import six
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session

from rattail.config import make_config, parse_list
from rattail.exceptions import ConfigurationError
from rattail.db.types import GPCType

from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from zope.sqlalchemy import register

import tailbone.db
from tailbone.auth import TailboneAuthorizationPolicy
from tailbone.config import csrf_token_name, csrf_header_name
from tailbone.util import get_effective_theme, get_theme_template_path


def make_rattail_config(settings):
    """
    Make a Rattail config object from the given settings.
    """
    rattail_config = settings.get('rattail_config')
    if not rattail_config:

        # initialize rattail config and embed in settings dict, to make
        # available for web requests later
        path = settings.get('rattail.config')
        if not path or not os.path.exists(path):
            raise ConfigurationError("Please set 'rattail.config' in [app:main] section of config "
                                     "to the path of your config file.  Lame, but necessary.")
        rattail_config = make_config(path)
        settings['rattail_config'] = rattail_config
    rattail_config.configure_logging()

    # configure database sessions
    if hasattr(rattail_config, 'rattail_engine'):
        tailbone.db.Session.configure(bind=rattail_config.rattail_engine)
    if hasattr(rattail_config, 'trainwreck_engine'):
        tailbone.db.TrainwreckSession.configure(bind=rattail_config.trainwreck_engine)
    if hasattr(rattail_config, 'tempmon_engine'):
        tailbone.db.TempmonSession.configure(bind=rattail_config.tempmon_engine)

    # create session wrappers for each "extra" Trainwreck engine
    for key, engine in rattail_config.trainwreck_engines.items():
        if key != 'default':
            Session = scoped_session(sessionmaker(bind=engine))
            register(Session)
            tailbone.db.ExtraTrainwreckSessions[key] = Session

    # Make sure rattail config object uses our scoped session, to avoid
    # unnecessary connections (and pooling limits).
    rattail_config._session_factory = lambda: (tailbone.db.Session(), False)

    return rattail_config


def provide_postgresql_settings(settings):
    """
    Add some PostgreSQL-specific settings to the app config.  Specifically,
    this enables retrying transactions a second time, in an attempt to
    gracefully handle database restarts.
    """
    try:
        import pyramid_retry
    except ImportError:
        settings.setdefault('tm.attempts', 2)
    else:
        settings.setdefault('retry.attempts', 2)


class Root(dict):
    """
    Root factory for Pyramid.  This is necessary to make the current request
    available to the authorization policy object, which needs it to check if
    the current request "is root".
    """

    def __init__(self, request):
        self.request = request


def make_pyramid_config(settings, configure_csrf=True):
    """
    Make a Pyramid config object from the given settings.
    """
    config = settings.pop('pyramid_config', None)
    if config:
        config.set_root_factory(Root)
    else:

        # we want the new themes feature!
        establish_theme(settings)

        settings.setdefault('pyramid_deform.template_search_path', 'tailbone:templates/deform')
        config = Configurator(settings=settings, root_factory=Root)

    # configure user authorization / authentication
    config.set_authorization_policy(TailboneAuthorizationPolicy())
    config.set_authentication_policy(SessionAuthenticationPolicy())

    # maybe require CSRF token protection
    if configure_csrf:
        rattail_config = settings['rattail_config']
        config.set_default_csrf_options(require_csrf=True,
                                        token=csrf_token_name(rattail_config),
                                        header=csrf_header_name(rattail_config))

    # Bring in some Pyramid goodies.
    config.include('tailbone.beaker')
    config.include('pyramid_deform')
    config.include('pyramid_mako')
    config.include('pyramid_tm')

    # bring in the pyramid_retry logic, if available
    # TODO: pretty soon we can require this package, hopefully..
    try:
        import pyramid_retry
    except ImportError:
        pass
    else:
        config.include('pyramid_retry')

    # Add some permissions magic.
    config.add_directive('add_tailbone_permission_group', 'tailbone.auth.add_permission_group')
    config.add_directive('add_tailbone_permission', 'tailbone.auth.add_permission')

    # and some similar magic for config views
    config.add_directive('add_tailbone_config_page', 'tailbone.app.add_config_page')

    return config


def add_config_page(config, route_name, label):
    """
    Register a config page for the app.
    """
    def action():
        pages = config.get_settings().get('tailbone_config_pages', [])
        pages.append({'label': label, 'route': route_name})
        config.add_settings({'tailbone_config_pages': pages})
    config.action(None, action)


def establish_theme(settings):
    rattail_config = settings['rattail_config']

    theme = get_effective_theme(rattail_config)
    settings['tailbone.theme'] = theme

    directories = settings['mako.directories']
    if isinstance(directories, six.string_types):
        directories = parse_list(directories)

    path = get_theme_template_path(rattail_config)
    directories.insert(0, path)
    settings['mako.directories'] = directories


def configure_postgresql(pyramid_config):
    """
    Add some PostgreSQL-specific tweaks to the final app config.  Specifically,
    adds the tween necessary for graceful handling of database restarts.
    """
    pyramid_config.add_tween('tailbone.tweens.sqlerror_tween_factory',
                             under='pyramid_tm.tm_tween_factory')


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    settings.setdefault('mako.directories', ['tailbone:templates'])
    rattail_config = make_rattail_config(settings)
    pyramid_config = make_pyramid_config(settings)
    pyramid_config.include('tailbone')
    return pyramid_config.make_wsgi_app()
