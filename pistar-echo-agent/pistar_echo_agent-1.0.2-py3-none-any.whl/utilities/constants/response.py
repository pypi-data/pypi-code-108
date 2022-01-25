"""
description: this module provides the constant status code.
"""


class STATUS_CODE:
    OK = 200
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500


class RESPONSE:
    BLOCK_ID = "block_id"
    TASK_START = "task_start_time"
    TASK_END = "task_end_time"
    LOG_PATHS = "executor_log_paths"
    IS_EXECUTED = "is_executed"
    TIMESTAMP = "timestamp"
    ERROR_CODE = "error_code"
    ERROR_MSG = "error_msg"
