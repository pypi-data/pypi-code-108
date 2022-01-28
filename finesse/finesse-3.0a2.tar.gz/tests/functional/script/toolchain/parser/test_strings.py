import pytest
from finesse.script.containers import KatScript, KatElement
from ..util import NAME, STRING, SPACE
from ..data import STRINGS


@pytest.mark.parametrize("string,_a,_b", STRINGS)
def test_string(parser, string, _a, _b):
    assert parser.parse(f"fake_element el1 {string}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[STRING(1, 18, string)],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )
