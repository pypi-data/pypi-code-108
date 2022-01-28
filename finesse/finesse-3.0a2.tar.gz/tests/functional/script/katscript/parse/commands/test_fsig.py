import pytest
from finesse.script.exceptions import KatScriptError


def test_fsig_default(model):
    assert model.fsig.f.value is None


@pytest.mark.parametrize("f", (1, 3.141, 10))
def test_fsig(model, f):
    model.parse(f"fsig({f})")
    assert float(model.fsig.f) == f


@pytest.mark.parametrize("f", (0, 0.0, -1, -3.141, -10, "'hi'", 1 + 2j))
def test_invalid_fsig(model, f):
    with pytest.raises(KatScriptError):
        model.parse(f"fsig({f})")
