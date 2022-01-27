# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
import typing as _t
from .. platform.library import scan_files


# Library Plugin interface:


def required_features() -> _t.List[str]:
    """
    Returns:
        Features required for enabling the library.
    """
    return []


def identifier() -> str:
    """
    Returns:
        Library identifier, which should be unique. See
        https://en.wikipedia.org/wiki/Reverse_domain_name_notation
    """
    return ''


def name() -> str:
    """
    Returns:
        Library name as shown in Library View, documentation etc.
    """
    return ''


def icon() -> str:
    """
    Returns:
        Path to icon file.
    """
    return ''


def description() -> str:
    """
    Returns:
        Brief description of the library.
    """
    return ''


def maintainer() -> str:
    """
    Returns:
        Maintainer. Format Name <email>.
    """
    return ''


def copyright() -> str:
    """
    Returns:
        Copyright.
    """
    return ''


def version() -> str:
    """
    Returns:

        Version. Format minor.major.micro
    """
    return ''


def nodes() -> _t.List[str]:
    """
    Returns:
        Paths to python files containing nodes.
    """
    return []


def flows() -> _t.List[str]:
    """
    Returns:
        Paths to python files containing flow nodes.
    """
    return []


def plugins() -> _t.List[str]:
    """
    Returns:
        Paths to python files containing node plugins.
    """
    return []


def migrations() -> _t.List[str]:
    """
    Returns:
        Paths to python files containing node migrations.
    """
    return []


def tags() -> _t.List['sympathy.api.nodeconfig.LibraryTags']:
    """
    Returns:
        Tags for organizing nodes in Library View.
    """
    return []


def types() -> _t.List['sympathy.api.typeutil.TypeAlias']:
    """
    Returns:
        Port type definitions.
    """
    return []


def examples_path() -> str:
    """
    Returns:
        Path to examples.
    """
    return ''


def repository_url() -> str:
    """
    Returns:
        URL to public source repository.
    """
    return ''


def documentation_url() -> str:
    """
    Returns:
        URL to public documentation.
    """
    return ''


def home_url() -> str:
    """
    Returns:
        URL to public home page.
    """
    return ''
