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


class WritebackError(AssertionError):
    pass


class WritebackReadOnlyError(WritebackError):
    pass


class SyTypeError(Exception):
    pass


class DatasetTypeError(SyTypeError):
    pass


def assert_exc(pred, exc=AssertionError, msg=None):
    if not pred:
        if msg:
            raise exc(msg)
        else:
            raise exc
