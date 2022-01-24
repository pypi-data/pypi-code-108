#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Masked version of LJM Communication for testing purposes.
"""

import logging
from collections import defaultdict
from numbers import Real
from queue import Queue
from typing import Union, Sequence

from hvl_ccb import comm

logger = logging.getLogger(__name__)


class MaskedLJMCommunication(comm.LJMCommunication):
    """
    Masks the LJMCommunication protocol disabling read and write to be able to test
    the functionality of devices without
    """

    def __init__(self, configuration):
        super().__init__(configuration)

        self._read_buffer = defaultdict(Queue)
        self._write_buffer = Queue()

    def read_name(self, *names: str, return_num_type=float):

        try:
            out = tuple(
                (
                    self._cast_read_value(
                        name,
                        self._read_buffer[name].get(),
                        return_num_type=return_num_type,
                    )
                    if not self._read_buffer[name].empty()
                    else return_num_type(0)
                )
                for name in names
            )
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            raise TypeError from e

        return out[0] if len(out) == 1 else out

    def write_name(
        self, name: Union[Sequence[str], str], value: Union[Sequence[object], object]
    ):

        if isinstance(name, str):
            name = [name]
            value = [value]

        for pair in zip(name, value):
            self._write_buffer.put(pair)

    def write_address(
        self, address: Union[Sequence[int], int], value: Union[Sequence[object], object]
    ):
        pass

    def put_name(self, name: str, value: object):
        # Note: labjack library returns `float` (`ctypes.c_double`?), even when `int`
        #       value is expected, but allow also in tests mock values with invalid type
        if isinstance(value, Real):
            value = float(value)
        self._read_buffer[name].put(value)

    def get_written(self):
        return self._write_buffer.get() if not self._write_buffer.empty() else None
