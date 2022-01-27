# Copyright (c) Qotto, 2021

"""
Request record
"""

from eventy.record.record import Record, RecordType

__all__ = [
    'Request',
]


class Request(Record):
    """
    Request implementation of the Record abstract base class
    """

    @property
    def type(self) -> RecordType:
        """
        Record type (REQUEST)

        :return: Type.REQUEST
        """

        return RecordType.REQUEST
