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
import typing
from . import plugins


# Editor Plugin interface:


def can_edit(filename=None):
    """
    Return True if plugin can edit filename and False otherwise.
    """
    raise NotImplementedError()


def can_debug(filename=None):
    """
    Return True if plugin can debug filename and False otherwise.
    """
    raise NotImplementedError()


def edit(filename=None):
    raise NotImplementedError()


def debug(filename):
    raise NotImplementedError()


# Editor plugins:

identifier = 'sympathy.editor.plugins'
_editors = plugins.Plugin(identifier, typing.Any)


def available_editors():
    return _editors.plugins().values()


# Utilities:

def can_edit_file(filename=None):
    return any(editor.can_edit(filename) for editor in available_editors())


def can_debug_file(filename=None):
    return any(editor.can_debug(filename) for editor in available_editors())


def edit_file(filename=None):
    for editor in available_editors():
        if editor.can_edit(filename):
            return editor.edit(filename)
    return False


def debug_file(filename=None):
    for editor in available_editors():
        if editor.can_debug(filename):
            return editor.debug(filename)
    return False
