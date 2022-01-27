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
from . import sybase


class sygeneric(sybase.sygroup):

    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        super(sygeneric, self).__init__(container_type,
                                        datasource or sybase.NULL_SOURCE)

    def source(self, other, shallow=False):
        pass

    def _writeback(self, datasource, link=None):
        # Transfer relies on direct compatiblity, for example, in the hdf5
        # datasource case both sources need to be hdf5 and the source needs to
        # be read only.
        if link:
            return False

        pass

    def __repr__(self):
        return "generic()"

    def __deepcopy__(self, memo=None):
        return self.__copy__()
