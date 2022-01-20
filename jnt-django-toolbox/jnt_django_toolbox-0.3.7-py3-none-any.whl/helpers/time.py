from datetime import timedelta


def seconds(**kwargs):
    """Get seconds from duration."""
    return timedelta(**kwargs).total_seconds()
