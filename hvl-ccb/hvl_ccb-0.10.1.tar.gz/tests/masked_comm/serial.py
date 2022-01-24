#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Masked version of SerialCommunication for testing purposes.
"""

from queue import Queue

from hvl_ccb.comm import SerialCommunication
from hvl_ccb.dev import (
    CryLasLaserSerialCommunication,
    FuGSerialCommunication,
    HeinzingerSerialCommunication,
    LuminoxSerialCommunication,
    NewportSMC100PPSerialCommunication,
    PfeifferTPGSerialCommunication,
)
from hvl_ccb.dev.technix import TechnixSerialCommunication


class LoopSerialCommunication(SerialCommunication):
    """
    Serial communication for the tests with "loop://" port. Masks `write` method
    and adds `put_text` method to put actual values for the serial communication
    protocol to read with the `read_text` method.
    """

    def __init__(self, configuration):
        super().__init__(configuration)

        self._write_buffer = Queue()

    def write(
        self,
        text: str,
    ):
        self._write_buffer.put(text)

    def put_text(self, text: str):
        # super().write(text)
        super().write_bytes(
            text.encode(encoding=self.config.encoding) + self.config.terminator
        )

    def write_bytes(self, data: bytes):
        self._write_buffer.put(data)

    def put_bytes(self, data: bytes):
        super().write_bytes(data)

    def get_written(self):
        return self._write_buffer.get() if not self._write_buffer.empty() else None


class CryLasLaserLoopSerialCommunication(
    CryLasLaserSerialCommunication, LoopSerialCommunication
):
    pass


class FuGLoopSerialCommunication(FuGSerialCommunication, LoopSerialCommunication):
    pass


class HeinzingerLoopSerialCommunication(
    HeinzingerSerialCommunication, LoopSerialCommunication
):
    pass


class LuminoxLoopSerialCommunication(
    LuminoxSerialCommunication, LoopSerialCommunication
):
    pass


class NewportLoopSerialCommunication(
    NewportSMC100PPSerialCommunication, LoopSerialCommunication
):
    pass


class PfeifferTPGLoopSerialCommunication(
    PfeifferTPGSerialCommunication, LoopSerialCommunication
):
    pass


class TechnixLoopSerialCommunication(
    TechnixSerialCommunication, LoopSerialCommunication
):
    pass
