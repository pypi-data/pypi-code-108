import finesse
from finesse.analysis.actions import Change, TemporaryParameters, Series, StoreModelAttr
import pytest


@pytest.mark.parametrize(
    "param,initial,value",
    [
        ("m1.phi", 0, 10),
        ("m1.phi", 11, -2),
        ("L0.P", 1, 0),
    ],
)
def test_temporary_parameters(param, initial, value):
    kat = finesse.Model()
    kat.parse(
        """
        l L0 P=1
        s s0 L0.p1 m1.p1
        m m1 R=0.99 T=0.01
        s CAV m1.p2 m2.p1 L=1
        m m2 R=0.991 T=0.009
    """
    )
    kat.set(param, initial)
    sol = kat.run(
        TemporaryParameters(Series(Change({param: value}), StoreModelAttr(param)))
    )
    assert sol.values[param] == value
    assert kat.get(param) == initial
