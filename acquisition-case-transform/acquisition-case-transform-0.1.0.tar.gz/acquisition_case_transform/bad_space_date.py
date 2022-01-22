import re

from casedate.base.us_uk import uk, us


def BadSPACEDATE_fix(m) -> str:
    return m.group("digit") + ", " + m.group("docket_date")


BadSPACEDATE = re.compile(
    rf""" # Simon, G.R. No. 9302829 July 1994
        (?P<digit>\d{{4,}}?) # without non-greedy qualifier, date would be 9 July 1994
        (?P<docket_date>
            {us}|{uk}
        )
    """,
    re.X | re.I,
)
