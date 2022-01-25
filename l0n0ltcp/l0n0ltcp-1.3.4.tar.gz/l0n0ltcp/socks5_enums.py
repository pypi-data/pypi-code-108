from enum import IntEnum


class Socks5ServerState(IntEnum):
    ReadMethods = 1
    ReadCmd = 2
    WaitConnect = 3
    TransData = 4