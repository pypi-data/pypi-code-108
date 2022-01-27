# Copyright (c) Qotto, 2021

"""
Event record
"""

from eventy.record.record import Record, RecordType

__all__ = [
    'Event',
]


class Event(Record):
    """
    Event implementation of the Record abstract base class
    """

    @property
    def type(self) -> RecordType:
        """
        Record type (EVENT)

        :return: Type.EVENT
        """
        return RecordType.EVENT
