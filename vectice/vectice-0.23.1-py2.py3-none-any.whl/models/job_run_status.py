from enum import EnumMeta


class JobRunStatus(EnumMeta):
    """
    Indicates the status of a run
    """

    CREATED = "CREATED"
    """
"""
    STARTED = "STARTED"
    """
"""
    SCHEDULED = "SCHEDULED"
    """
"""
    COMPLETED = "COMPLETED"
    """
"""
    FAILED = "FAILED"
    """
"""
    ABORTED = "ABORTED"
    """
"""
