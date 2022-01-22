import re


def BadGR_fix(m) -> str:
    digits = (
        m.group("digit") + m.group("other_digit")
        if m.group("other_digit")
        else m.group("digit")
    )
    return "G.R. No. " + digits


BadGR = re.compile(
    r"""
        (
            G
            \s*
            \.?
            \s*
            R
            \.?
        )
        \s*
        No
        s? # letter s
        [,.]? # notice comma
        \s* # can be no space between 'no.' and digit'
        (?P<digit>
            \d+
        )
        \s*
        (?P<other_digit>
            [\d\-]+
        )?
    """,
    re.X,
)
