import pytest
from finesse.script.containers import KatScript, KatElement
from ..util import NAME, BOOLEAN, SPACE
from ..data import BOOLEANS


@pytest.mark.parametrize("value,_a,_b", BOOLEANS)
def test_boolean(parser, value, _a, _b):
    assert parser.parse(f"fake_element el1 {value}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[BOOLEAN(1, 18, value)],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )
