class PackEnum(object):
    PARAMETER = 0x0100
    COUNTER = 0x0200
    COUNTER_1 = 0x0201
    PROFILE = 0x0300
    ACTIVESTACK = 0x0400
    TEXT = 0x0700
    ERROR_SNAP = 0x0800
    ERROR_SNAP_1 = 0x0801
    REALTIME_USER = 0x0f00
    REALTIME_USER_1 = 0x0f01

    STAT_SERVICE = 0x0900
    STAT_GENERAL = 0x0910
    STAT_SQL = 0x0a00
    STAT_HTTPC = 0x0b00
    STAT_ERROR = 0x0c00
    STAT_METHOD = 0x0e00
    STAT_TOP_SERVICE = 0x1000
    STAT_REMOTE_IP = 0x1100
    STAT_USER_AGENT = 0x1200
    STAT_USER_AGENT_1 = 0x1201

    EVENT = 0x1400
    HITMAP = 0x1500
    HITMAP_1 = 0x1501
    EXTENSION = 0x1600

    COMPOSITE = 0x1700

    @staticmethod
    def create(p):
        return None

class EventLevel(object):
    FATAL = 30
    WARNING = 20
    INFO = 10
    NONE = 0
