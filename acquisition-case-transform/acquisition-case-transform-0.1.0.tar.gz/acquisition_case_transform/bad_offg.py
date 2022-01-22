import re
from enum import Enum

VOL = r"(?P<vol>\d{1,3})"
PAGE = r"(?P<page>\d{1,4})"


def BadOFFG_fix(m) -> str:
    return m.group("vol") + " OG " + m.group("page")


class BadOFFG(Enum):
    @property
    def pattern(self):
        return re.compile(self.value, re.X)
