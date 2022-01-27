# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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
# When adding a new editor, also add it to gui/create_editor.
# Also add to dict in layers.py


class Base(object):
    """Base object for other editors to inherit."""

    def __init__(self, *args, **kwargs):
        self.options = lambda: None
        self.property_object = None
        self.value_range = None
        self.tags = set()
        self.get = lambda: self.property_object.get()
        self.set = lambda x: self.property_object.set(x)

    def init(self):
        pass


class String(Base):
    """String editor."""

    pass


class MultiLineString(Base):
    """Multi line string editor."""

    pass


class DataSource(Base):
    """Editor for choosing data source."""

    pass


class Integer(Base):
    """Integer editor."""

    pass


class Float(Base):
    """Float editor."""

    pass


class Color(Base):
    """Color editor."""

    pass


class Boolean(Base):
    """Boolean editor."""

    pass


class ImmutableList(Base):
    """Immutable list editor using ComboBox."""

    current_index = 0

    def __init__(self, options_function):
        super(ImmutableList, self).__init__(options_function)
        # The options are always fetched using a function.
        assert hasattr(options_function, '__call__')
        self.options = options_function

        # We need to update current_index as well when setting the value
        def new_setter(x):
            self._old_setter(x)
            self.init()
        self._old_setter = self.set
        self.set = new_setter

    def init(self):
        # Initialize index for combo box. Fallback on zero.
        try:
            self.current_index = self.options().index(self.get())
        except (AttributeError, ValueError):
            self.current_index = -1


class ColorScale(Base):
    """Select a color scale using ComboBox."""

    pass


class Image(Base):
    """Select an image using a file selector."""

    pass


class EditorTags(object):
    """Tags for giving editors different properties."""

    force_update_after_edit = 0,
    force_rebuild_after_edit = 1
