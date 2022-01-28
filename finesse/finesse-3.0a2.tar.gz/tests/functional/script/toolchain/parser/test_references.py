import pytest
from finesse.script.containers import KatScript, KatElement
from ..util import NAME, SPACE, REFERENCE


@pytest.mark.parametrize("reference", ("&m1.T", "&l1.P", "&mod1.p1.o.q"))
def test_binary_expression(parser, reference):
    assert parser.parse(f"fake_element el1 {reference}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[REFERENCE(1, 18, reference)],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )
