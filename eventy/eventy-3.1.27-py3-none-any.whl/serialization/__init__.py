# Copyright (c) Qotto, 2021

"""
Record serialization package
"""

from typing import Any

from eventy.record import Record

__all__ = [
    'RecordSerializer',
]


class RecordSerializer:
    """
    Record serializer interface
    """

    def encode(self, record: Record) -> Any:
        """
        Encode a record

        Raises:
            SerializationError
        """
        raise NotImplementedError

    def decode(self, encoded: Any) -> Record:
        """
        Decode a record

        Raises:
            SerializationError
        """
        raise NotImplementedError
