import enum


class OMLogLevel(enum.Enum):
    NORMAL = None
    STATS = "-lv=LOG_STATS"
    INIT = "-lv=LOG_INIT"
    RES_INIT = "-lv=LOG_RES_INIT"
    SOLVER = "-lv=LOG_SOLVER"
    EVENTS = "-lv=LOG_EVENTS"
    NONLIN_SYS = "-lv=LOG_NONLIN_SYS"
    ZEROCROSSINGS = "-lv=LOG_ZEROCROSSINGS"
    DEBUG = "-lv=LOG_DEBUG"
