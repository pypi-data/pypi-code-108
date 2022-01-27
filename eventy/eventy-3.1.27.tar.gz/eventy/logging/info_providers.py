# Copyright (c) Qotto, 2021

"""
<<<<<<< HEAD
Provides information to log records

Logging filters to inject trace ids in LogRecord instances

The python logging API allows to add attributes to log records using filters
"""

from logging import LogRecord

from eventy.trace_id import correlation_id_var, request_id_var

__all__ = [
    'correlation_id_provider',
    'request_id_provider',
]


def correlation_id_provider(log_record: LogRecord) -> bool:
    """
    Add ``correlation_id`` field in the log record

    :param log_record: log record to annotate
    :return: True (not really a filter)
    """
    if not hasattr(log_record, 'correlation_id'):
        setattr(log_record, 'correlation_id', correlation_id_var.get())
    return True


def request_id_provider(log_record: LogRecord) -> bool:
    """
    Add ``request_id`` field in the log record

    :param log_record: log record to annotate
    :return: True (not really a filter)
    """
    if not hasattr(log_record, 'request_id'):
        setattr(log_record, 'request_id', request_id_var.get())
    return True
