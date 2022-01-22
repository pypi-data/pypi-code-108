import re
from enum import Enum

VOL = r"(?P<vol>\d{1,3})"
PAGE = r"(?P<page>\d{1,4})"


def BadSCRA_fix(m) -> str:
    return m.group("vol") + " SCRA " + m.group("page")


class BadSCRA(Enum):
    # 174, SCRA 464 [1989]
    # 205, SCRA 266
    vol_comma = rf"""
        {VOL}
        \s*
        , # vol comma needs removal
        \s*
        SCRA
        \s*
        {PAGE}
    """

    # (X v. Y, June 28, 1974, 57 SCRA, 508-509)
    # 30 SCRA, 454
    # Academia, et al., 198 SCRA .705 (1991).
    page_comma = rf"""
        {VOL}
        \s*
        SCRA
        \s*
        (,|\.) # page comma needs removal
        \s*
        {PAGE}
    """

    # 183 SCRA [347]
    in_bracket_page = rf"""
        {VOL}
        \s*
        SCRA
        \s*
        \[{PAGE}\] # note brackets
    """

    # page 865 of 280 SCRA.
    page_word = rf"""
        page
        \s+
        {PAGE}
        \s+
        of
        \s+
        {VOL}
        \s+
        SCRA
    """

    # (181 SCRA at 207-208)
    at_page = rf"""
        {VOL}
        \s*
        SCRA
        \s+
        at
        \s*
        {PAGE}
    """

    # (133 SCRA p. 82)
    # (58 SCRA, p. 450)
    # (44  SCRA, p. 176)
    p_page = rf"""
        {VOL}
        \s*
        SCRA
        ,?
        \s+
        p\.
        \s*
        {PAGE}
    """

    # 105 SCRA6 [1981]
    no_space = rf"""
        {VOL}
        \s*
        SCRA # no space
        \s*
        {PAGE}
    """

    incorrect_SRA = rf"""
        {VOL}
        \s*
        (
            SçRA|
            SRA|
            SRCA
        )
        \s*
        {PAGE}

    """

    @property
    def pattern(self):
        return re.compile(self.value, re.X)
