import re

from casedate.base.us_uk import uk, us


def BadPROMDATE_fix(m) -> str:
    return ", " + m.group("docket_date")


BadPROMDATE = re.compile(
    rf""" # G.R. No. 122629, promulgated December 2, 1998"
        ,
        \s*
        (
            prom
            (
                \.|
                ulgated
            )
        )
        \s*
        (?P<docket_date>
            {us}|{uk}
        )
    """,
    re.X | re.I,
)
