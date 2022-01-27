# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Type validation module"""


def valid_int_id(int_id: int) -> bool:
    """Validates an ID value as a signed 32-bit integer used
    in ID fields in MySQL tables.

    :param int_id: ID number to validate
    :return: True or False, based on if the integer falls inclusively
        between 0 and 2147483647
    """
    try:
        if not int_id:
            return False

        int_id_ = int(int_id)
    except ValueError:
        return False

    # Minimum value of a signed INT in MySQL/MariaDB is 0 and the
    # maximum value of signed INT type in MySQL/MariaDB is (2**31) - 1,
    # or 2147483647
    return 0 <= int_id_ <= (2**31 - 1)
