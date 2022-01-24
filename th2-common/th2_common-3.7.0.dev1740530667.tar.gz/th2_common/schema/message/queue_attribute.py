import enum


class QueueAttribute(enum.Enum):
    FIRST = 'first'
    SECOND = 'second'
    SUBSCRIBE = 'subscribe'
    PUBLISH = 'publish'
    PARSED = 'parsed'
    RAW = 'raw'
    EVENT = 'event'
    STORE = 'store'
