import pytest
from finesse.env import show_tracebacks
from finesse.exceptions import FinesseException
from ..util import escape_full


@pytest.fixture
def finesse_exception():
    """A function that throws a :class:`.FinesseException`."""

    def excfunc():
        raise FinesseException("__test__")

    return excfunc


@pytest.mark.parametrize(
    "tracebacks,error",
    (
        (True, "\n__test__"),
        (False, ("\t(use finesse.tb() to see the full traceback)\n" "__test__")),
    ),
)
def test_show_traceback(finesse_exception, tracebacks, error):
    # NOTE: there is still a traceback shown in addition to the "use finesse.tb()"
    # message when Finesse is run from a non-Jupyter terminal and tracebacks are
    # switched off, because in such an environment the _render_traceback_ method of the
    # exception where the traceback is suppressed is ignored. This test is therefore not
    # technically testing the intended behaviour, but only a proxy.
    show_tracebacks(tracebacks)
    with pytest.raises(FinesseException, match=escape_full(error)):
        finesse_exception()
