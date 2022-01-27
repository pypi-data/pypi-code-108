# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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
import itertools


def object_enumerator():
    """
    Workaround intended for QAbstractItemModel.createIndex
    which does not accept arbitrary python objects in PySide2 5.12.

    Instead, specify internal id. For this we use id(object).  Since this can
    be a 32-bit integer on some architectures, we track of all ids and count up
    for new ones.
    """
    objects = {}
    counter = itertools.count(1)

    def inner(obj):
        ident = id(obj)
        res = objects.get(ident)

        if res is None:
            res = next(counter)
            objects[ident] = res
        return res
    return inner
