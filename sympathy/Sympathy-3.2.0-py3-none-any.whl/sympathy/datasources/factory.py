# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
"""Factory module for datasources."""
from . hdf5.dstypes import types as hdf5
from . text.dstypes import types as text


class DatasourceFactory(object):
    """Returns a data source object for the required data source."""
    _datasource_from_scheme = {
        'hdf5': hdf5,
        'text': text,
    }

    def from_type_dict(self, type_cls, data):
        scheme = data['scheme']
        return self._datasource_from_scheme[scheme].from_type_dict(
            type_cls, data)


factory = DatasourceFactory()
