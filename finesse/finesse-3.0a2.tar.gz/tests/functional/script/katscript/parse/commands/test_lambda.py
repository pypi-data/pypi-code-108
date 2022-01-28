import pytest
from finesse.script.exceptions import KatScriptError


def test_lambda_default(model):
    assert model.lambda0 == 1064e-9


@pytest.mark.parametrize("lambda0", (1, 3.141, 10))
def test_lambda(model, lambda0):
    model.parse(f"lambda({lambda0})")
    assert float(model.lambda0) == lambda0


@pytest.mark.xfail(reason="lambda0 validation not implemented yet")
@pytest.mark.parametrize("lambda0", (0, 0.0, -1, -3.141, -10, "'hi'", 1 + 2j))
def test_invalid_lambda(model, lambda0):
    with pytest.raises(KatScriptError):
        model.parse(f"lambda({lambda0})")
