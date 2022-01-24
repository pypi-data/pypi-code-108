from django.dispatch import Signal


log_created: Signal = Signal()
"""Fires when new log entry created.

Args:
    instance: Instance of created log object.
"""

tracking_enter: Signal = Signal()
"""Fires when new tracking code added to a stack.

Args:
    code (str): Tracking code that was added.
"""

tracking_exit: Signal = Signal()
"""Fires when new tracking code removed from a stack.

Args:
    code (str): Tracking code that was removed.
"""
