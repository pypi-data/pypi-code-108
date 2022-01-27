# This file is part of Sympathy for Data.
# Copyright (c) 2017-2018, Combine Control Systems AB
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
"""
API for working with the Json type.

Import this module like this::

    from sympathy.api import json

Class :class:`json.File`
--------------------------
.. autoclass:: File
   :members:
   :special-members:
"""
import json
import numpy as np

from .. utils import filebase
from .. utils.context import inherit_doc


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):
            try:
                return obj.tolist()
            except Exception:
                pass
        elif isinstance(obj, np.ndarray):
            try:
                return obj.tolist()
            except Exception:
                pass
        return super().default(obj)


@filebase.typeutil('sytypealias json = sytext')
@inherit_doc
class File(filebase.TypeAlias):
    """
    A Json structure.

    Any node port with the *Json* type will produce an object of this type.
    """
    def set(self, data):
        self._data.set(json.dumps(data, cls=NumpyEncoder))

    def get(self):
        return json.loads(self._data.get() or 'null')

    def source(self, other, shallow=False):
        self.set(other.get())

    @classmethod
    def viewer(cls):
        from .. platform import json_viewer
        return json_viewer.JsonViewer

    @classmethod
    def icon(cls):
        return 'ports/json.svg'
