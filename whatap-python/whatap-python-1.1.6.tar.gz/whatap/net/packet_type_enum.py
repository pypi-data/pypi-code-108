class PacketTypeEnum(object):
    TX_BLANK = 0
    TX_START = 1
    TX_DB_CONN = 2
    TX_DB_FETCH = 3
    TX_SQL = 4
    TX_SQL_START = 5
    TX_SQL_END = 6

    TX_HTTPC = 7
    TX_HTTPC_START = 8
    TX_HTTPC_END = 9

    TX_ERROR = 10
    TX_MSG = 11
    TX_METHOD = 12

    # secure msg
    TX_SECURE_MSG = 13

    TX_END = 255

    TX_PARAM = 30
    ACTIVE_STACK = 40
    ACTIVE_STATS = 41
    DBCONN_POOL = 42

    EVENT = 50
