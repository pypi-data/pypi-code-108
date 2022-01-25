"""
description: this module provides the function parse file name
"""
from .time_util import get_current_milliseconds_time


def get_convert_path(file_path, testcase_name):
    """
    get new file path from old file path and test case name
    """
    file_prefix = str(file_path)[:-3]
    testcase_name = testcase_name.replace("/", "_").replace("\\", "_")
    new_file_path = f"{file_prefix}_{testcase_name}_{get_current_milliseconds_time()}.py"
    return new_file_path
