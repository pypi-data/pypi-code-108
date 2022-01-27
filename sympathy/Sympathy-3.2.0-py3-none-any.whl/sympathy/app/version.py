# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from packaging import version as pkg_version

from sympathy import version as sy_version
from . import config

major = sy_version.major
minor = sy_version.minor
micro = sy_version.micro
status = sy_version.status

edition_name = sy_version._edition_name
version_tuple = sy_version.version_tuple
version = sy_version.version
build = status

parsed_version = pkg_version.Version(version)
parsed_base_version = pkg_version.Version(parsed_version.base_version)


def application_name():
    return 'Sympathy for Data'


def window_title():
    base_name = application_name()

    if edition_name:
        return f'{base_name} {edition_name}'
    else:
        return base_name


_base_url = sy_version._base_url()


def application_url():
    """Return the URL to the developer website."""
    return f'{_base_url}/'


def documentation_url():
    """Return the URL to the documentation."""
    return f'{_base_url}/doc/{major}.{minor}.{micro}/'


def privacy_url():
    """Return the URL to the privacy section."""
    return f'{_base_url}/legal/latest/product/{major}.{minor}.{micro}/privacy/'


def application_copyright():
    """Return the name of the copyright holder."""
    return 'Combine Control Systems AB'


def email_bugs():
    """Return the email address for bug reports."""
    return 'support@sympathyfordata.com'


def email_contribution():
    """Return the email address to use for those who want to contribute."""
    return 'support@sympathyfordata.com'


def license_info():
    """Return a dict with info about the license."""
    return config.active()['license']
