import numpy as np
import pytest
from poisson_approval import Asymptotic, isnan, isposinf


def test_limit():
    assert isnan(Asymptotic(mu=np.nan, nu=51, xi=69).limit)
    assert isnan(Asymptotic(mu=0, nu=np.nan, xi=69).limit)
    assert isposinf(Asymptotic(mu=0, nu=51, xi=69).limit)


def test_add():
    asymptotic = Asymptotic(mu=np.nan, nu=51, xi=69) + Asymptotic(mu=42, nu=51, xi=69)
    assert isnan(asymptotic.mu)
    assert isnan(asymptotic.nu)
    assert isnan(asymptotic.xi)

    asymptotic = Asymptotic(mu=42, nu=51, xi=69) + Asymptotic(mu=42, nu=np.nan, xi=69)
    assert asymptotic.mu == 42
    assert isnan(asymptotic.nu)
    assert isnan(asymptotic.xi)


def test_isclose():
    assert not Asymptotic(mu=42, nu=51, xi=69).look_equal(144)
    with pytest.raises(ValueError):
        Asymptotic(mu=np.nan, nu=51, xi=69).look_equal(Asymptotic(mu=42, nu=51, xi=69))


def test_str_small_magnitudes():
    asymptotic = Asymptotic(mu=-2E-10, nu=0, xi=0)
    assert str(asymptotic) == 'exp(- 2e-10 n + o(1))'


def test_limit_ratio_with_small_magnitudes():
    numerator = Asymptotic(mu=-2E-10, nu=0, xi=0)
    denominator = Asymptotic(mu=-1E-10, nu=0, xi=0)
    ratio = numerator / denominator
    assert ratio.limit == 0
