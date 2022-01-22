import re
from enum import Enum

VOL = r"(?P<vol>\d{1,3})"
PAGE = r"(?P<page>\d{1,4})"


def BadPHIL_fix(m) -> str:
    return m.group("vol") + " Phil. " + m.group("page")


class BadPHIL(Enum):
    # 42, Phil. 205
    vol_comma = rf"""
        {VOL}
        \s*
        , # vol comma needs removal
        \s*
        Phil\.
        \s*
        {PAGE}
    """

    # Dilan v. Dulfo, 364 Phil.103, March 11, 1999
    no_space = rf"""
        {VOL}
        \s*
        Phil\. # no space
        \s*
        {PAGE}
    """

    @property
    def pattern(self):
        return re.compile(self.value, re.X)
