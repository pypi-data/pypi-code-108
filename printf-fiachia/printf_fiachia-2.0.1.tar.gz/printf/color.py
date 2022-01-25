# 定义颜色，方便简打
class __Color:
    def __init__(self):
        self.BLACK = "black"
        self.RED = "red"
        self.GREEN = "green"
        self.YELLOW = "yellow"
        self.BLUE = "blue"
        self.PURPLERED = "purple-red"
        self.CYANINE = "cyanine"
        self.WHITE = "white"
        self.DEFAULT = "default"


class __Effect:
    def __init__(self):
        self.HIGHLIGHT = "highlight"
        self.UNDERLINE = "underline"
        self.FLASH = "flash"
        self.BACKWHITE = "backwhite"
        self.UNSHOW = "unshow"
        self.DEFAULT = "default"


class __Type:
    def __init__(self):
        self.ERROR = "error"
        self.WARNING = "warning"
        self.SUCCESS = "success"
        self.DATA = "data"
        self.SYSTEM = "system"
        self.NORMAL = "normal"


COLOR = __Color()
BACKGROUND = __Color()
EFFETC = __Effect()
TYPE = __Type()
"""
BLACK = "black"
RED = "red"
GREEN = "green"
YELLOW = "yellow"
BLUE = "blue"
PURPLERED = "purple-red"
CYANINE = "cyanine"
WHITE = "white"
DEFAULT = "default"

HIGHLIGHT = "highlight"
UNDERLINE = "underline"
FLASH = "flash"
BACKWHITE = "backwhite"
UNSHOW = "unshow"

ERROR = "error"
WARNING = "warning"
SUCCESS = "success"
DATA = "data"
SYSTEM = "system"
NORMAL = "normal"
"""
