"""
description: this module provides the function get time.
"""
from time import localtime, strftime


def get_current_time_format():
    """
    description: this function is used to get current time.
    """
    return strftime("%Y-%m-%d %H:%M:%S", localtime())
