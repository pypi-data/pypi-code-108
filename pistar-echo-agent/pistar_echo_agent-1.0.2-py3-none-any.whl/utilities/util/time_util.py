"""
description: this module provides the function get current different format time
"""
import time
from datetime import datetime


def get_current_time_format():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


def get_current_milliseconds_time():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]


def get_current_timestamp():
    return int(time.time() * 1000)
