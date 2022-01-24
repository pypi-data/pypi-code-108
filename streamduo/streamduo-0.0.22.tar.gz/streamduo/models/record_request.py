from enum import Enum


class ReadRecordRequestType(Enum):
    """
    Enum class to ensure accuracy of read record request types
    """
    SAMPLE = 'SAMPLE'
    UNREAD = 'UNREAD'
    READ_SINCE_RECORD_ID = 'READ_SINCE_RECORD_ID'
    READ_SINCE_TIMESTAMP = 'READ_SINCE_TIMESTAMP'
    SINGLE = 'SINGLE'
    LAST_N = 'LAST_N'