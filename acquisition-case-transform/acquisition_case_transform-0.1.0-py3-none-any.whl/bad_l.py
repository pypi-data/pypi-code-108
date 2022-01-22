import re


def BadL_fix(m) -> str:
    digits = (
        m.group("digit") + m.group("other_digit")
        if m.group("other_digit")
        else m.group("digit")
    )
    return "No. L-" + digits


# Casiano, L- 15309, February 16, 1961
BadL = re.compile(
    r"""
    (
        No\.
        \s
    )?
    L
    \s*
    \-?
    \s*
    (?P<digit>
        \d+
    )
    \s*
    (?P<other_digit>
        \d+
    )?

    """,
    re.X,
)
