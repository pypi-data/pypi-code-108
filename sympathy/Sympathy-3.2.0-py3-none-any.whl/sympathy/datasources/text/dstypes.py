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
"""Text type constructor module."""
from . dslist import TextList as DsList
from . dsdict import TextDict as DsDict
from . dsrecord import TextRecord as DsRecord
from . dstable import TextTable as DsTable
from . dstext import TextText as DsText
from . dslambda import TextLambda as DsLambda
from ... platform.types import (TypeList,
                                TypeDict,
                                TypeRecord,
                                TypeTuple,
                                TypeTable,
                                TypeText,
                                TypeFunction,
                                TypeAlias)


class TextFactory(object):
    """
    Returns Text type constructors.
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


types = TextFactory()
