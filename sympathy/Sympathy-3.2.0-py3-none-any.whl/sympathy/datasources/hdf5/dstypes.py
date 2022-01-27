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
"""HDF5 type constructor module."""
from . dslist import Hdf5List as DsList
from . dsdict import Hdf5Dict as DsDict
from . dsrecord import Hdf5Record as DsRecord
from . dstable import Hdf5Table as DsTable
from . dstext import Hdf5Text as DsText
from . dslambda import Hdf5Lambda as DsLambda
from ... platform.types import (TypeList,
                                TypeDict,
                                TypeRecord,
                                TypeTuple,
                                TypeTable,
                                TypeText,
                                TypeFunction)


class Hdf5Factory(object):
    """
    Returns HDF5 type constructors.
    Creates typed instances.
    """
    _cls_lookup = {
        TypeList: DsList,
        TypeDict: DsDict,
        TypeRecord: DsRecord,
        TypeTuple: DsRecord,
        TypeTable: DsTable,
        TypeText: DsText,
        TypeFunction: DsLambda,
    }

    def from_type_group(self, type_cls, group, **kwargs):
        ds = self._cls_from_type(type_cls)
        return ds(self, group=group, **kwargs)

    def from_type_dict(self, type_cls, file_info):
        ds = self._cls_from_type(type_cls)
        return ds(self, file_info=file_info)

    def _cls_from_type(self, type_cls):
        """Return datasource constructor according to type_cls."""
        # Construct the child element.
        cls = self._cls_lookup.get(type_cls)
        if cls is None:
            raise Exception(f'Unknown content type: {type_cls}')
        return cls


types = Hdf5Factory()
