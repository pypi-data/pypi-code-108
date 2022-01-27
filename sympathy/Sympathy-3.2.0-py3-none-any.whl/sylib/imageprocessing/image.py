# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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

import os
import numpy as np
from sympathy.api import typeutil
from sympathy.utils import port

# Full path to the directory where this file is located.
_directory = os.path.abspath(os.path.dirname(__file__))


@typeutil.typeutil(
    'sytypealias image = (meta_table: sytable, image_table: sytable)')
class File(typeutil.TypeAlias):
    """Represents images loaded into Sympathy."""

    def _extra_init(self, gen, data, filename, mode, scheme, source):
        pass

    @classmethod
    def viewer(cls):
        from . import image_viewer
        return image_viewer.ImageViewer

    @classmethod
    def icon(cls):
        return os.path.join(_directory, 'port_image.svg')

    def source(self, other, shallow=False):
        """
        Update self with a deepcopy of the data from other, without keeping the
        old state.

        self and other must be of the exact same type.
        """
        self._data.source(other._data, shallow=shallow)

    def set_image(self, image):
        if len(image.shape) < 3:
            image = image.reshape(image.shape+(1,))
        self._data.meta_table.set_column("shape", np.r_[image.shape])
        self._data.image_table.set_column("image", image.ravel())

    def get_image(self):
        if ('shape' in self._data.meta_table.columns() and
            'image' in self._data.image_table.columns()):
            shape = self._data.meta_table.get_column('shape')
            image = self._data.image_table.get_column('image').reshape(shape)
            return image
        else:
            return np.zeros((1, 1, 1))

    @property
    def name(self):
        return self._data.meta_table.name

    @name.setter
    def name(self, value):
        self._data.meta_table.name = value

    @property
    def attrs(self):
        return self._data.meta_table.attrs

    def attr(self, name):
        return self._data.meta_table.attr(name)

    def set_attr(self, name, value):
        self._data.meta_table.set_attr(name, value)

    @property
    def im(self):
        return self.get_image()

    @property
    def width(self):
        if 'shape' in self._data.meta_table.columns():
            shape = self._data.meta_table.get_column('shape')
            return shape[1]
        else:
            return 1

    @property
    def height(self):
        if 'shape' in self._data.meta_table.columns():
            shape = self._data.meta_table.get_column('shape')
            return shape[0]
        else:
            return 1

    def names(self, kind=None, **kwargs):
        res = []
        if kind == 'calc':
            res = ['.im', '.width', '.height']
        elif kind == 'name':
            res = [self.name()]

        return res

    def types(self, kind=None, **kwargs):
        res = []
        if kind == 'calc':
            res = [self.get_image().dtype, np.dtype(int), np.dtype(int)]
        elif kind == 'name':
            res = [self.name()]
        return res


def Image(description, name=None, n=None):
    return port.CustomPort('image', description, name=name)

def Images(description, name=None, n=None):
    return port.CustomPort('[image]', description, name=name)
