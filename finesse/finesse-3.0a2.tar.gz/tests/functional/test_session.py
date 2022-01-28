"""Tests for prints and warnings made with the top level session object."""

import pytest
from finesse import env


@pytest.mark.parametrize(
    "verbosity,prints,warns",
    (
        (-10, False, False),
        (-1, False, False),
        (0, False, False),
        (1, False, False),
        (9, False, False),
        (10, False, True),
        (11, False, True),
        (19, False, True),
        (20, True, True),
        (21, True, True),
        (29, True, True),
    ),
)
def test_session(capsys, recwarn, verbosity, prints, warns):
    """Test that the user's verbosity setting is obeyed in printing and warning."""
    printmsg = "print"
    warnmsg = "warning"

    env.session_instance().verbosity = verbosity
    env.info(printmsg)
    env.warn(warnmsg)

    captured = capsys.readouterr()

    if prints:
        assert captured.out == f"{printmsg}\n"
    else:
        assert not captured.out

    if warns:
        assert len(recwarn) == 1
        warning = recwarn.pop()
        assert str(warning.message) == warnmsg
    else:
        assert not recwarn
