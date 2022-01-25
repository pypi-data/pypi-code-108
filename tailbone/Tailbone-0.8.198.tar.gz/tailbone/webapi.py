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
Tailbone Web API
"""

from __future__ import unicode_literals, absolute_import

from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy

from tailbone import app
from tailbone.auth import TailboneAuthorizationPolicy


def make_rattail_config(settings):
    """
    Make a Rattail config object from the given settings.
    """
    rattail_config = app.make_rattail_config(settings)
    return rattail_config


def make_pyramid_config(settings):
    """
    Make a Pyramid config object from the given settings.
    """
    pyramid_config = Configurator(settings=settings, root_factory=app.Root)

    # configure user authorization / authentication
    pyramid_config.set_authorization_policy(TailboneAuthorizationPolicy())
    pyramid_config.set_authentication_policy(SessionAuthenticationPolicy())

    # always require CSRF token protection
    pyramid_config.set_default_csrf_options(require_csrf=True,
                                            token='_csrf',
                                            header='X-XSRF-TOKEN')

    # bring in some Pyramid goodies
    pyramid_config.include('tailbone.beaker')
    pyramid_config.include('pyramid_tm')
    pyramid_config.include('cornice')

    # bring in the pyramid_retry logic, if available
    # TODO: pretty soon we can require this package, hopefully..
    try:
        import pyramid_retry
    except ImportError:
        pass
    else:
        pyramid_config.include('pyramid_retry')

    # add some permissions magic
    pyramid_config.add_directive('add_tailbone_permission_group', 'tailbone.auth.add_permission_group')
    pyramid_config.add_directive('add_tailbone_permission', 'tailbone.auth.add_permission')

    return pyramid_config


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    rattail_config = make_rattail_config(settings)
    pyramid_config = make_pyramid_config(settings)

    # bring in some Tailbone
    pyramid_config.include('tailbone.subscribers')
    pyramid_config.include('tailbone.api')

    return pyramid_config.make_wsgi_app()
