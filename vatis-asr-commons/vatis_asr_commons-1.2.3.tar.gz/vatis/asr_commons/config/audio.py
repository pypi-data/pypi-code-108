from enum import Enum


class Language(Enum):
    ro_RO: str = 'ro_RO'
    en_GB: str = 'en_GB'


class SampleRate(Enum):
    RATE_16000: int = 16000


class Channel(Enum):
    ONE: int = 1


class BitDepth(Enum):
    BIT_16: int = 2
