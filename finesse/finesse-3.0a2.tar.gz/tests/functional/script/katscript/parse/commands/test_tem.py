import pytest


@pytest.fixture
def tem_model(model):
    model.parse(
        """
        l L0 P=1
        gauss gL0 L0.p1.o w0=1m z=0
        modes(x, maxtem=1)
        """
    )
    return model


def test_tem_default(tem_model):
    assert tem_model.L0.power_coeffs == tem_model.L0.DEFAULT_POWER_COEFFS


def test_tem_default_mode_nondefault_factor(tem_model):
    """Default modes with non-default factor."""
    tem_model.parse("tem(L0, 0, 0, factor=0.5)")
    assert tem_model.L0.power_coeffs == {(0, 0): (0.5, 0)}


def test_tem(tem_model):
    tem_model.parse(
        """
        tem(L0, 0, 0, factor=0)
        tem(L0, 1, 0, factor=1)
        tem(L0, 1, 1, factor=0.5, phase=35)
        """
    )

    assert tem_model.L0.power_coeffs == {
        (0, 0): (0, 0),
        (1, 0): (1, 0),
        (1, 1): (0.5, 35),
    }
