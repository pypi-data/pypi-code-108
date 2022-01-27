# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
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
from sympathy.api import typeutil
from sympathy.utils import port
from sympathy import typeutils
# Full path to the directory where this file is located.
_directory = os.path.abspath(os.path.dirname(__file__))


@typeutil.typeutil('sytypealias geojson = json')
class File(typeutils.json.File):
    """GeoJSON type."""

    @classmethod
    def viewer(cls):
        from . import geojson_viewer
        return geojson_viewer.GeoJSONViewer

    @classmethod
    def icon(cls):
        return os.path.join(_directory, 'geojson.svg')


def GeoJSON(description, name=None):
    return port.CustomPort('geojson', description, name=name)
