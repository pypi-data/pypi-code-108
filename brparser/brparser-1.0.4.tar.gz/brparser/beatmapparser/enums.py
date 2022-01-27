from enum import IntFlag

class FileSection(IntFlag):
    UNKNOWN = 0
    GENERAL = 1 << 0
    COLOURS = 1 << 1
    EDITOR = 1 << 2
    METADATA = 1 << 3
    TIMINGPOINTS = 1 << 4
    EVENTS = 1 << 5
    HITOBJECTS = 1 << 6
    DIFFICULTY = 1 << 7
    VARIABLES = 1 << 8
    ALL = GENERAL | COLOURS | EDITOR | METADATA | TIMINGPOINTS | EVENTS | HITOBJECTS | DIFFICULTY | VARIABLES

class HitObjectType(IntFlag):
    NORMAL = 1
    SLIDER = 2
    NEWCOMBO = 4
    NORMALNEWCOMBO = 5
    SLIDERNEWCOMBO = 6
    SPINNER = 8
    COLOURHAX = 112
    HOLD = 128
