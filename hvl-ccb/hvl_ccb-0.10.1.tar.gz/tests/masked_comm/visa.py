#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
VISA masked communication protocol module.
"""

from collections import defaultdict
from queue import Queue
from typing import Union, Tuple

from hvl_ccb.comm import VisaCommunication


class MaskedVisaCommunication(VisaCommunication):
    """
    Masked version of VisaCommunication to simulate messages.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._read_buffer = defaultdict(Queue)
        self._write_buffer = Queue()

        self.stb = 0

    def open(self) -> None:
        pass

    def close(self):
        pass

    def write(self, *commands: str) -> None:
        if '*OPC' in commands:
            # operation complete request set, immediately reply
            self.put_name('*ESR?', '1')

        for command in commands:
            self._write_buffer.put(command)

    def query(self, *commands: str) -> Union[str, Tuple[str, ...]]:
        out = [
            self._read_buffer[command].get() if not self._read_buffer[command].empty()
            else '0'
            for command in commands
        ]

        return out[0] if len(out) == 1 else tuple(out)

    def spoll(self) -> int:
        return self.stb

    def put_name(self, command: str, string: str) -> None:
        self._read_buffer[command].put(string)

    def get_written(self) -> Union[str, None]:
        return self._write_buffer.get() if not self._write_buffer.empty() else None
