# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
major = 3
minor = 2
micro = 0
status = ''
version_tuple = (major, minor, micro, status)

# Intended to be substituted to identify different editions.
_edition_name = ""


def get_version(local_version_identifiers=None):
    local = local_version_identifiers or []

    if local:
        version = '{}.{}.{}{}+{}'.format(*version_tuple, '.'.join(local))
    else:
        version = '{}.{}.{}{}'.format(*version_tuple)
    return version


# TODO(erik): investigate if it is enough to set build_local_version in the
# wheel definition. Which can be passed as argument instead of by editing the
# file.
version = get_version()


def package_name():
    """
    Internal use only
    """
    name = 'Sympathy'

    if _edition_name:
        name = f'{name} {_edition_name}'
    return name


def _base_url():
    """Internal use only."""
    return 'https://www.sympathyfordata.com'


def _license_url(license_version=None):
    if license_version is None:
        license_version = version
    return f'{_base_url()}/legal/latest/product/{license_version}/eula/'


__version__ = version
