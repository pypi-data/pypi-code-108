import pytest
from ..util import IMPLICITLINEEND, ENDMARKER, REFERENCE


@pytest.mark.parametrize("string", ("&m1", "&m2.T", "&m3.phi", "&m4.p1.o.q",))
def test_reference(tokenizer, string):
    assert list(tokenizer.tokenize(string)) == [
        REFERENCE(1, 1, string),
        IMPLICITLINEEND(1, 1 + len(string)),
        ENDMARKER(2),
    ]
