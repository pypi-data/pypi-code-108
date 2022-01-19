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
Rattail config extension for Tailbone
"""

from __future__ import unicode_literals, absolute_import

from rattail.config import ConfigExtension as BaseExtension
from rattail.db.config import configure_session

from tailbone.db import Session


class ConfigExtension(BaseExtension):
    """
    Rattail config extension for Tailbone.  Does the following:

     * Adds the rattail config object to the constructor kwargs for the
       underlying Session factory.

     * Configures the main Tailbone database session so that it records
       changes, if the config file so dictates.
    """
    key = 'tailbone'

    def configure(self, config):
        Session.configure(rattail_config=config)
        configure_session(config, Session)

        # provide default theme selection
        config.setdefault('tailbone', 'themes', 'default, falafel')
        config.setdefault('tailbone', 'themes.expose_picker', 'true')


def csrf_token_name(config):
    return config.get('tailbone', 'csrf_token_name', default='_csrf')


def csrf_header_name(config):
    return config.get('tailbone', 'csrf_header_name', default='X-CSRF-TOKEN')


def global_help_url(config):
    return config.get('tailbone', 'global_help_url')


def protected_usernames(config):
    return config.getlist('tailbone', 'protected_usernames')
