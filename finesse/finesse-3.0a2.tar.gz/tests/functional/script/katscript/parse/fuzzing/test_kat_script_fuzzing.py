from hypothesis import given, settings
from finesse.script import parse
from ......util import kat_script_line


@given(line=kat_script_line())
@settings(deadline=1000)  # See #292.
def test_kat_script_line_fuzzing(line):
    parse(line)
