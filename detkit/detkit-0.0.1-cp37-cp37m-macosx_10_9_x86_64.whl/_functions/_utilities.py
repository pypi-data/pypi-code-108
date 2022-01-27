# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


__all__ = ['get_data_type_name']


# ==================
# get data type name
# ==================

def get_data_type_name(data):
    """
    Returns the typename of data as string.
    """

    if data.dtype == 'float32':
        data_type_name = b'float32'
    elif data.dtype == 'float64':
        data_type_name = b'float64'
    elif data.dtype == 'float128':
        data_type_name = b'float128'

    return data_type_name
