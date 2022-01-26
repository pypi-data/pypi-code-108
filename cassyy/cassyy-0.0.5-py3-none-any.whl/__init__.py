"""
Simple Apereo Central Authentication Service (CAS) client
"""
import logging as _logging

from .core import (
    CASClient,
    CASError,
    CASInvalidServiceError,
    CASInvalidTicketError,
    CASUser,
)

__version__ = '0.0.5'

__all__ = [
    'CASClient',
    'CASUser',
    'CASError',
    'CASInvalidServiceError',
    'CASInvalidTicketError',
]

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
