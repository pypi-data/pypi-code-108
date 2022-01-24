from django.dispatch import Signal


log_stored = Signal()
"""Fires when new log entry stored in database.

Args:
    instance: Instance of stored in database log object.
"""
