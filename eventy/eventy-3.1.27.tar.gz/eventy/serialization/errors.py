# Copyright (c) Qotto, 2021

"""
Record serialization errors
"""

__all__ = [
    'SerializationError',
    'UnknownRecordTypeError',
]


class SerializationError(Exception):
    """
    Base for all serialization errors
    """


class UnknownRecordTypeError(SerializationError):
    """
    Record type unknown (not EVENT, REQUEST, or RESPONSE)
    """

    def __init__(self, record_type: str) -> None:
        super().__init__(f'Unknown record type {record_type}')
