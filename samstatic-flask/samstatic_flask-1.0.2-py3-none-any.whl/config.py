from enum import Enum

class Option(str, Enum):
    DEACTIVE = 'DEACTIVE'
    ALL = 'ALL'
    ALLOWED = 'ALLOWED'
    DISALLOWED = 'DISALLOWED'