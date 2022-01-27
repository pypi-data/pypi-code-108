# Copyright (c) Qotto, 2021

from typing import Union

from eventy.record import Record, Event, Request, Response
from eventy.serialization import RecordSerializer


class DummySerializer(RecordSerializer):
    """
    Warning: for tests purposes, does not encode in bytes.
    """

    def encode(self, record: Record) -> bytes:
        return record  # type: ignore

    def decode(self, encoded: bytes) -> Union[Event, Request, Response]:
        return encoded  # type: ignore
