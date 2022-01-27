# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
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
Utilities for using masked arrays to represent missing data.
"""
import numpy as np


def max(array):
    if isinstance(array, np.ma.MaskedArray):
        if array.dtype.kind in 'Mm':
            # Workaround np.max always returns NaT for datetime array with
            # masked values.
            array = array.compressed()
    return np.max(array)


def min(array):
    return np.min(array)


def _getdata_arrays(arrays):
    return [np.ma.getdata(a) for a in arrays]


def _getmaskarray_arrays(arrays):
    return [np.ma.getmaskarray(a) for a in arrays]


def asarray(arrays):
    # Preserve mask in asarray in contrast with numpy 1.19+
    # which looses it, at least for masked str array.
    if any(np.ma.is_masked(a) for a in arrays):
        masks = _getmaskarray_arrays(arrays)
        datas = _getdata_arrays(arrays)
        res = np.ma.masked_array(
            data=np.asarray(datas),
            mask=np.asarray(masks))
    else:
        res = np.asarray(arrays)
    return res


def astype(column, dtype):
    """
    Return column.astype(dtype).
    If column is masked, only data is converted returning
    a new masked array with default fill value.
    """
    if isinstance(column, np.ma.core.MaskedArray):
        column = np.ma.masked_array(
            data=column.data.astype(dtype),
            mask=column.mask)
    else:
        column = column.astype(dtype)
    return column
